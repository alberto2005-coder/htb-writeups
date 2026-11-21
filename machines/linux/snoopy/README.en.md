---
machine: Snoopy
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, dns, bind, mattermost, git-apply, cve-2023-23946, clamav, cve-2023-20052, privesc]
---

# Snoopy — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`download?file=` has directory traversal; BIND's configuration and TSIG keys are read, the DNS zone is updated and `snoopy.htb` password-reset emails are redirected to a local server. That opens Mattermost; a server-provisioning slash command is pointed at an SSH honeypot and hands over `cbrown`'s credentials. `cbrown` can run `git apply -v` as `sbrown` under a very restrictive regex; CVE-2023-23946 writes outside the repository through a symlink created by the patch itself and reaches `sbrown`. For root, `sudo` allows `clamscan --debug` on a specific directory; CVE-2023-20052 (XXE when parsing DMG) executes as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,53,80 <IP>
```

- `22`: OpenSSH 8.9p1 Ubuntu.
- `53`: ISC BIND 9.18.12.
- `80`: nginx 1.18.0.

```bash
echo '<IP> snoopy.htb mattermost.snoopy.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://snoopy.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

The site has downloads through `download?file=`. An LFI wordlist confirms traversal with `....//` sequences; it reads `/etc/passwd` and the BIND configuration (`/etc/bind/named.conf.local` and keys). It also reveals the Mattermost vhost and the mail domain.

The DNS zone allows updates with the read TSIG keys. An MX record is added or the reset email destination is changed so it reaches a local server.

```bash
python3 -m aiosmtpd -n -l 0.0.0.0:25
nsupdate -k <TSIG_KEY>
```

## Foothold

A Mattermost account password reset is requested and the email arrives at the local server. The link changes the password and logs into Mattermost. Inside, a slash command provisions servers: it is configured to connect to a local SSH honeypot (Cowrie). The command sends credentials to the honeypot, which records them; they belong to `cbrown`.

## Lateral movement

`cbrown` can run a single command as `sbrown`:

```text
(sbrown) PASSWD: /usr/bin/git ^apply -v [a-zA-Z0-9.]+$
```

The regex forbids spaces, so the patch must be a single argument. Git 2.34.1 is vulnerable to CVE-2023-23946: a patch can create a symlink and write through it outside the repository. A patch creates the link and writes to `/home/sbrown/.ssh/authorized_keys`, applied with `sudo -u sbrown git apply -v <patch>`.

## Privilege escalation

`sbrown` can run as root:

```text
(root) NOPASSWD: /usr/local/bin/clamscan ^--debug /home/sbrown/scanfiles/[a-zA-Z0-9.]+$
```

ClamAV 1.0.0 is vulnerable to CVE-2023-20052: the DMG parser processes XML without disabling external entities, enabling XXE. A crafted `.dmg` is placed in `scanfiles` and `clamscan` runs; the external entity reads root's SSH key.

```bash
sudo /usr/local/bin/clamscan --debug /home/sbrown/scanfiles/<FILE>.dmg
```

CVE-2023-20032 (HFS+ overflow) is mentioned in the box documentation but is not exploited.

## Evidence

- Traversal in `download?file=` and BIND configuration read.
- TSIG keys and DNS zone update.
- Reset email received and Mattermost access.
- Slash command pointed at the honeypot and `cbrown` credentials.
- `sudo -l` with `git apply` and the CVE-2023-23946 patch.
- `sudo -l` with `clamscan` and a DMG with XXE.
- `id` with UID 0.

## Lessons learned

- An LFI reads service configuration and keys, not just `/etc/passwd`.
- TSIG keys allow DNS changes and email redirection.
- Server-provisioning slash commands can send credentials to a controlled destination.
- A `sudo` regex does not prevent exploiting a binary vulnerability.
- ClamAV also parses disk images and can be vulnerable to XXE.
- Do not confuse the two ClamAV CVEs: the exploited one is the DMG XXE.

## Mitigations and detection

- Validate download paths and block traversal.
- Protect TSIG keys and restrict DNS updates.
- Verify reset email destinations and use single-use tokens.
- Review slash commands and limit their network destinations.
- Update Git and ClamAV; do not allow `git apply` or `clamscan` through `sudo`.
- Alert on DNS updates, reset emails and DMG scans.

## References

- [0xdf — Snoopy](https://0xdf.gitlab.io/2023/09/23/htb-snoopy.html)
- [IppSec — Snoopy](https://www.youtube.com/watch?v=6tn30O0SjVQ)
- [Hack The Box — Snoopy](https://app.hackthebox.com/machines/snoopy)
- [NVD — CVE-2023-23946](https://nvd.nist.gov/vuln/detail/CVE-2023-23946)
- [NVD — CVE-2023-20052](https://nvd.nist.gov/vuln/detail/CVE-2023-20052)
- [Knowledge — git apply and CVE-2023-23946](../../../knowledge/linux/git-apply-cve-2023-23946.en.md)
