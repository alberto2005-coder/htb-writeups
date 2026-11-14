---
machine: Mist
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, pluck, adcs, esc13, petitpotam, shadow-credentials]
---

# Mist — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Pluck CMS 4.7.18 allows reading `data/settings.php` and recovering the administrator password; a malicious PHP module is uploaded and `svc_web` is obtained on MS01. A shared directory with links provides execution as `Brandon.Keywarp`, and after PetitPotam and shadow credentials on `svc_cabackup`, ESC13 grants Certificate Managers and Backup Operators. The DC hives are copied and Administrator hashes extracted.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,88,389,445 <IP>
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -u http://<DOMAIN>/FUZZ
```

## Enumeration

- MS01 runs Apache/PHP with Pluck CMS 4.7.18.
- The read parameter reaches `data/settings.php`.
- `C:\Common Applications` is writable and shared over SMB.

## Initial access

Read the Pluck configuration and crack the administrator hash. With the session, upload a ZIP module containing a webshell, executed as `svc_web`. On MS01, overwrite `Notepad.lnk` in the shared directory with a PowerShell shortcut; when `Brandon.Keywarp` opens it, his session is obtained.

## Privilege escalation

With LDAP signing disabled, PetitPotam coerces MS01 authentication and relays it to LDAP to obtain `svc_ca$`. Certipy adds a shadow credential to `svc_cabackup`, and the ESC13 templates `ManagerAuthentication` and `BackupSvcAuthentication` grant Certificate Managers and ServiceAccounts. `reg.py backup` copies SAM/SYSTEM/SECURITY, `secretsdump` extracts the Administrator hash and the DC is accessed.

## Evidence

- Access to `settings.php` and a webshell as `svc_web`.
- Malicious link and `Brandon.Keywarp` shell.
- ESC13 certificates, copied hives and Administrator shell.

## Lessons learned

- Old CMS software and file permissions compromise the whole host.
- LDAP signing and channel binding are essential controls.
- ESC13 combines templates and groups in a way that is hard to see without ADCS auditing.

## Mitigation and detection

- Update Pluck and restrict share writes.
- Require LDAP signing, channel binding and EPA.
- Audit templates with OID group links and limit Enrollment Agents.

## References

- [0xdf — Mist](https://0xdf.gitlab.io/2024/10/26/htb-mist.html)
- [IppSec — Mist](https://www.youtube.com/watch?v=5osU3Igzv_Y)
- [Hack The Box — Mist](https://app.hackthebox.com/machines/mist)
