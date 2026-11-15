---
machine: Browsed
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, chrome, extension, ssrf, pycache]
---

# Browsed — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Chrome debug logs reveal an internal Gitea instance and a Flask application on localhost. A malicious extension performs SSRF against Flask and Bash arithmetic injection yields RCE. Escalation poisons the `__pycache__` bytecode used by a sudo script.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,3000,5000 <IP>
ffuf -u http://browsed.htb -H "Host: FUZZ.browsed.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
# Chrome logs
curl -s http://browsed.htb/logs/chrome_debug.log | grep -iE "gitea|localhost|token"
# Extension: host_permissions for http://localhost:*/*
# SSRF and Bash arithmetic
curl -s "http://127.0.0.1:5000/render?expr=$((1+1))"
# Pycache
find / -type d -name __pycache__ -writable 2>/dev/null
python3 -c "import py_compile; py_compile.compile('payload.py', cfile='__pycache__/module.cpython-311.pyc')"
sudo /usr/bin/python3 /opt/app/script.py
```

## Enumeration

- Chrome with `--remote-debugging-port` and accessible logs.
- Internal Gitea and a Flask app bound to `127.0.0.1`.
- Sudo script importing modules from a writable directory.

## Initial access

Read the Chrome logs to obtain the Gitea URL and Flask port. Install a controlled extension that requests the victim localhost; the vulnerable parameter reaches a Bash arithmetic expression and runs commands.

## Privilege escalation

`sudo -l` shows a Python script importing a local module. The `__pycache__` directory is writable; compile a malicious `.pyc` with the same name and the next sudo run loads it, yielding root.

## Evidence

- Chrome log with the debug URL.
- SSRF request to internal Flask and shell callback.
- Malicious `.pyc` loaded by the sudo script.

## Lessons learned

- Chrome remote debugging exposes history and cookies.
- An extension with host permissions can reach loopback.
- Python trusts bytecode when the `.py` is unchanged.

## Mitigation and detection

- Do not expose the debugging port and clear its logs.
- Review extensions and isolate internal services.
- Mount `__pycache__` read-only and use `PYTHONDONTWRITEBYTECODE`.

## References

- [0xdf — Browsed](https://0xdf.gitlab.io/2026/03/28/htb-browsed.html)
- [Chrome — Extension permissions](https://developer.chrome.com/docs/extensions/develop/concepts/declare-permissions)
- [Hack The Box — Browsed](https://app.hackthebox.com/machines/browsed)
