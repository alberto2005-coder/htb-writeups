---
machine: Agile
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, flask, file-read, werkzeug, chrome-debug, sudoedit, cve-2023-22809]
---

# Agile — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Flask password-manager application has a file-read flaw and runs Werkzeug in debug mode. The debugger yields execution, a database password leads to SSH, and a test instance with remote Chrome debugging exposes another user's session. `sudoedit` vulnerable to CVE-2023-22809 then edits a virtualenv file that root loads at login.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH and Nginx serving a Flask application.
- `superpass.htb` and a test host.
- `feroxbuster` finds download endpoints and a debug console.

## Enumeration

- File download accepts a user-controlled path.
- Werkzeug runs in debug mode and exposes the interactive console.
- Source and database contain user credentials.
- A Chrome process with remote debugging belongs to the test instance.

## Foothold

File read recovers source and configuration. The Werkzeug console, protected by the Flask debug PIN, opens after calculating or leaking the PIN; commands then run as the service user.

```bash
curl -s "http://superpass.htb/download?file=..."
```

## Privilege escalation

The database password gives SSH access. The test Chrome debug port can be queried to list tabs and recover session cookies or credentials. The second user may run `sudoedit`; CVE-2023-22809 allows adding arbitrary files to the edit and modifying the virtualenv that root sources at login.

```bash
sudo -l
sudoedit /etc/hosts /home/<USER>/.venv/lib/python3.*/site-packages/sitecustomize.py
```

## Evidence

- Response reading a path outside the allowed directory.
- Werkzeug console and `id` output.
- Chrome debug port showing tabs and cookies.
- `sudo -l` showing `sudoedit` and root execution.

## Lessons learned

- Flask debug mode must never be exposed.
- An unauthenticated Chrome debugger is a gateway to active sessions.
- CVE-2023-22809 turns `sudoedit` into arbitrary write.

## Mitigations and detection

- Disable debug and the Werkzeug console in production.
- Close debug ports and isolate test browsers.
- Update sudo and restrict `sudoedit` to specific files.
- References: HTB Agile, 0xdf, NVD CVE-2023-22809.

## References

- <https://www.hackthebox.com/machines/Agile>
- <https://0xdf.gitlab.io/2023/08/05/htb-agile.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-22809>
- <https://attack.mitre.org/techniques/T1190/>
