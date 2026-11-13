---
machine: GreenHorn
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, pluck-cms, gitea, webshell, depix, credential-recovery]
---

# GreenHorn — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An exposed Gitea instance leaks the configuration and admin password for Pluck CMS. Panel access allows uploading a PHP module and executing code. The Gitea database yields another account; a PDF with a pixelated password leads to root.

## Recon

```bash
nmap -Pn -sC -sV -p22,80,3000 <IP>
```

- SSH, HTTP and Gitea on 3000.
- Vhosts: `greenhorn.htb` and `git.greenhorn.htb`.

## Enumeration

- The main site runs Pluck CMS 4.7.18.
- Gitea hosts a public repository with the site configuration.
- The repository exposes credentials or a hash for the Pluck panel.
- The panel is `/admin.php`.

## Foothold

With the admin account, a malicious module is uploaded. Pluck installs modules as PHP files and executes them from the module directory.

```bash
# Package a module containing the execution PHP and upload it from the panel
curl -s -b cookies.txt "http://greenhorn.htb/admin.php?action=installmodule"
```

The module returns code execution as `www-data`.

## Lateral movement

The `gitea.db` database stores Gitea account hashes. The hash for `git` is extracted and cracked offline.

```bash
sqlite3 gitea.db "select name,passwd_hash_algo,passwd from user;"
ssh git@greenhorn.htb
```

## Privilege escalation

The `git` home contains a PDF with root's password pixelated. The image is processed with Depix to recover the characters.

```bash
python3 depix.py -p blurred.png -s search_image.png -o recovered.png
su root
```

## Evidence

- Exposed repository and configuration file.
- PHP module and `id` output.
- Gitea hash and SSH access.
- PDF and recovered password, redacted.

## Lessons learned

- A public repository can leak secrets even when the main site looks small.
- CMS modules are executable code.
- Pixelation is not cryptographic protection for a credential.

## Mitigations and detection

- Do not publish configurations or credentials in repositories.
- Restrict module installation and validate module content.
- Rotate credentials and use a secret manager.
- Monitor uploads to module directories and unusual access to `gitea.db`.

## References

- <https://www.hackthebox.com/machines/greenhorn>
- <https://github.com/spipm/Depix>
- <https://attack.mitre.org/techniques/T1505/003/>
- <https://attack.mitre.org/techniques/T1552/>
