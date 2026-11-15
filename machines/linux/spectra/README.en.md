---
machine: Spectra
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, wordpress, plugin, initctl, chromeos]
---

# Spectra — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The website leads to WordPress and the panel allows installing or editing a plugin for RCE. An auto-login file grants another user; `initctl` with sudo launches a job as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443 <IP>
wpscan --url http://spectra.htb --enumerate u,vp
# WordPress panel: edit a plugin with a webshell
curl -s http://spectra.htb/wp-content/plugins/<PLUGIN>/shell.php?cmd=id
# Auto-login
find / -name "*autologin*" 2>/dev/null
cat /opt/autologin
sudo -l
sudo initctl start <JOB>
```

## Enumeration

- WordPress with an accessible admin panel.
- Editable plugins and a privileged account.
- `initctl` available with sudo in a ChromeOS-like environment.

## Initial access

Enumerate users and plugins; with panel credentials, add a plugin with a webshell or edit an existing one. Visiting the plugin executes code as `nginx` or `www-data`.

## Privilege escalation

An auto-login file contains another user's credentials. That user can run `initctl` with sudo; create a job that starts a shell and obtain root.

## Evidence

- Plugin with a webshell and execution.
- Auto-login with the second user's credentials.
- `sudo initctl` running a job and root shell.

## Lessons learned

- The WordPress panel is code execution by design.
- Auto-login files are plaintext credentials.
- `initctl` with sudo can launch privileged processes.

## Mitigation and detection

- Restrict plugin installation and panel access.
- Do not store auto-login on the filesystem.
- Limit `initctl` and review sudo rules.

## References

- [0xdf — Spectra](https://0xdf.gitlab.io/2021/06/26/htb-spectra.html)
- [WordPress — Plugin API](https://developer.wordpress.org/plugins/)
- [Hack The Box — Spectra](https://app.hackthebox.com/machines/spectra)
