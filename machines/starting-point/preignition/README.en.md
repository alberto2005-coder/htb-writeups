---
machine: Preignition
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
tags: [linux, web, gobuster, default-credentials]
---

# Preignition — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available (Starting Point), publishable.
> Reference notes. No real flags or credentials.

## TL;DR

An nginx serving an "under construction" page plus an **admin panel** linked from nowhere. Directory discovery finds `/admin.php`, and the panel takes **`admin:admin`**. The flag is inside. No command execution, no escalation: it is pure web enumeration and default credentials.

## Recon

```bash
nmap -sC -sV <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH
80/tcp  http  nginx 1.14.2
```

The front page is only a template saying "website is under construction".

## Enumeration

```bash
gobuster dir -u http://<IP>/ -w /usr/share/seclists/Discovery/Web-Content/common.txt -x php
```

```text
/admin.php            (Status: 200)
```

`feroxbuster -u http://<IP> -x php` gets there too, and `robots.txt` sometimes announces the panel.

## Access

```text
http://<IP>/admin.php
username: admin
password: admin
```

After logging in, the page itself prints the flag:

```text
<flag>
```

## Evidence (redacted)

```text
/admin.php  ->  <flag>
```

## Lessons

- A hidden panel is not a protected panel: content discovery finds it in seconds.
- Default credentials (`admin:admin`) remain the top cause of access in sample applications.
- Mitigation: remove sample panels from production, enforce strong passwords with MFA, rate limit and lock out on failures.
- Detection: 404 spikes per user and successful logins from new IPs.
