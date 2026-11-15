---
machine: Scepter
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, nfs, adcs, esc14, dcsync]
---

# Scepter — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An unauthenticated NFS share exposes PFX certificates. One provides domain access; password-change permissions and two AD CS ESC14 variants lead to DCSync and domain control.

## Reconnaissance

```bash
nmap -Pn -sCV -p111,2049,88,389,445 <IP>
showmount -e <IP>
mount -t nfs <IP>:/export /mnt/nfs
# AD CS
certipy find -u <USER>@<DOMAIN> -p "<PASS>" -dc-ip <DC> -vulnerable
certipy auth -pfx <CERT>.pfx -dc-ip <DC>
bloodyAD --host <DC> -d <DOMAIN> -u <USER> -p "<PASS>" set password <TARGET> "<NEWPASS>"
```

## Enumeration

- NFS exported without authentication with PFX files.
- Active Directory with AD CS and writable `altSecurityIdentities`.
- Permissions to change another user's password.

## Initial access

Mount the NFS share and recover the PFX files. `certipy auth` uses the certificate to obtain a TGT; with the resulting account, enumerate permissions and identify the AD CS path.

## Privilege escalation

Change the password of a user with write permissions and obtain their context. ESC14 maps a certificate to a privileged account through `altSecurityIdentities`; request the certificate and use it for DCSync.

## Evidence

- PFX recovered from NFS.
- TGT issued with `certipy auth`.
- ESC14 certificate and DCSync dump.

## Lessons learned

- Unauthenticated NFS can expose cryptographic material.
- AD CS must be audited beyond ESC1–ESC8.
- Poorly managed `altSecurityIdentities` breaks the trust model.

## Mitigation and detection

- Restrict NFS exports and protect PFX files.
- Audit templates, permissions and `altSecurityIdentities`.
- Enforce least privilege on password changes.

## References

- [0xdf — Scepter](https://0xdf.gitlab.io/2025/07/19/htb-scepter.html)
- [SpecterOps — ESC14](https://posts.specterops.io/adcs-esc14-abuse-14d1a58b8b5a)
- [Hack The Box — Scepter](https://app.hackthebox.com/machines/scepter)
