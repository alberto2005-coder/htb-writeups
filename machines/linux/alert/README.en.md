---
machine: Alert
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, xss, markdown, file-read, cron, php]
---

# Alert — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Markdown viewer allows HTML and JavaScript injection; the administrator bot visits the link and runs an XSS that reads internal pages. A directory traversal in `messages.php` retrieves the `.htpasswd` for `statistics.alert.htb`, whose hash cracks to SSH access as `albert`. A root cron runs a PHP web monitor with a writable configuration file, allowing a SUID bash to be created.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://<DOMAIN> -H "Host: FUZZ.<DOMAIN>"
```

## Enumeration

- The site converts Markdown to HTML and preserves embedded HTML.
- `statistics.alert.htb` requests basic authentication.
- The contact form sends a URL to the administrator bot.

## Initial access

Publish Markdown with a `<script>` that calls `fetch` on `messages.php?file=../../../../var/www/statistics.alert.htb/.htpasswd` and sends the result to an attacker server. The bot runs it and the hash for `albert` is obtained, cracked and reused over SSH.

## Privilege escalation

`/opt/website-monitor` runs as root from cron. One of its included files is writable by `albert`; add a line that copies bash to `/tmp`, makes it root-owned and SUID, then run it to read the flag.

## Evidence

- Bot request containing `.htpasswd`.
- Cracked hash and SSH access as `albert`.
- Modified configuration file and executed SUID bash.

## Lessons learned

- Markdown that allows raw HTML widens the XSS surface.
- Internal panels often trust password files reachable through traversal.
- A root cron over editable code is a direct escalation.

## Mitigation and detection

- Sanitize generated HTML and apply CSP.
- Keep authentication files outside the document root.
- Run the monitor read-only and as an unprivileged user.

## References

- [0xdf — Alert](https://0xdf.gitlab.io/2025/03/22/htb-alert.html)
- [IppSec — Alert](https://www.youtube.com/watch?v=zSBEfW46zd0)
- [Hack The Box — Alert](https://app.hackthebox.com/machines/alert)
