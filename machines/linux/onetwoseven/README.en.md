---
machine: OneTwoSeven
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, sftp, symlink, plugin-upload, apt, mitm]
---

# OneTwoSeven — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A hosting provider grants SFTP access without a shell. Symlinks expose the administration panel and credentials; a plugin upload bypass installs a webshell as `www-admin-data`. The sudo rule allows `apt-get update/upgrade` and preserves `http_proxy`; a fake repository is served and the `telnet` package is poisoned to execute code as root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,60080 <IP>
ssh -p 22 <USER>@<IP>
```

## Enumeration

- Port 22 only offers SFTP; 60080 is filtered externally.
- The panel shows a default user and a plugin manager.
- `/etc/apt/sources.list.d/onetwoseven.list` points to a custom repository.

## Initial access

Create symlinks in the SFTP directory pointing at panel files and read them through the web server. Log in to the panel on 60080 with `ots-admin` credentials and forward the port over SSH. Plugin upload disables the button, but adding the expected parameter directly to the request allows a ZIP with PHP to be uploaded and run as `www-admin-data`.

## Privilege escalation

`sudo -l` allows `apt-get update` and `apt-get upgrade`, and `env_keep` preserves `http_proxy`. Run a local proxy, answer for `packages.onetwoseven.htb` with a fake `Release`/`Packages`, and publish a `telnet` package with a malicious `postinst`. `apt-get upgrade` installs it as root and runs the script.

## Evidence

- Symlinks visible from the web listing.
- Panel access and webshell as `www-admin-data`.
- apt requests reaching the proxy and `postinst` execution.

## Lessons learned

- Symlinks in a file service can cross into the document root.
- Disabling a button does not remove the endpoint.
- A user-controlled apt proxy breaks the trust chain.

## Mitigation and detection

- Chroot or jail SFTP and forbid symlinks outside the home.
- Validate package and MIME on the server, not only in the UI.
- Do not preserve proxies in sudo and sign repositories.

## References

- [0xdf — OneTwoSeven](https://0xdf.gitlab.io/2019/08/31/htb-onetwoseven.html)
- [IppSec — OneTwoSeven](https://www.youtube.com/watch?v=EXuEDHFjS9E)
- [Hack The Box — OneTwoSeven](https://app.hackthebox.com/machines/onetwoseven)
