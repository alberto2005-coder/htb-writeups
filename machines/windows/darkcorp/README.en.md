---
machine: DarkCorp
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, roundcube, postgresql, ntlm-relay, adidns, shadow-credentials, sssd, gpo]
---

# DarkCorp — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Three hosts: a Debian web/mail server, a Windows web server and a DC. RoundCube XSS steals admin mail and reveals a subdomain; a reset and PostgreSQL SQLi give RCE. A cracked PGP backup gives domain access; from WEB-01, NTLM is relayed to LDAP, an ADIDNS record is created, PrinterBug is used and a silver ticket is obtained. The chain continues with task credentials, DPAPI, spray, shadow credentials, UPN spoofing, SSSD cache and GPO abuse to Domain Admin.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `drip.htb` is a Debian host with nginx, SSH and mail.
- `ffuf` finds `mail.drip.htb` and the admin dashboard.
- The environment includes `WEB-01` and `DC-01` on the internal network.

## Enumeration

- RoundCube is vulnerable to CVE-2024-42009: an email with XSS executes when opened.
- Send the payload to admin `bcase` and exfiltrate his mail, which reveals the dashboard subdomain.
- Password reset and SQLi in the login get into the dashboard.

## Foothold

The SQLi confirms PostgreSQL. With superuser rights, `COPY ... TO PROGRAM` or `archive_command` runs commands and yields a `postgres` shell.

```sql
COPY (SELECT '') TO PROGRAM 'id';
```

## Lateral movement

A PGP backup holds `ebelford`'s hash; crack it and use SSH. That account also reaches the `WEB-01` status portal, which performs checks and NTLM authentication.

- Relay NTLM to LDAP as `svc_acc`, a `DNSADMINS` member.
- Create an ADIDNS record for `DC-01` pointing to the attacker.
- PrinterBug forces `WEB-01` to authenticate; the relay grants a silver ticket for Administrator on `WEB-01`.

## Privilege escalation

On `WEB-01`, recover credentials from a scheduled task and decrypt a DPAPI credential. Spraying gets another account, which can request shadow credentials over a user with a matching `.adm` account; UPN spoofing returns admin access on `drip`. From root on `drip`, read SSSD cached credentials and pivot to the DC. The final user modifies a GPO and becomes Domain Admin.

## Evidence

- RoundCube CVE-2024-42009 and admin mail.
- PostgreSQL SQLi and RCE.
- `ebelford` hash and SSH access.
- NTLM relay, ADIDNS, PrinterBug and silver ticket.
- Tasks, DPAPI, spray, shadow credentials, UPN spoofing, SSSD and GPO.

## Lessons learned

- Webmail XSS can expose the rest of the chain.
- PostgreSQL superuser allows RCE through several paths.
- Backups and mail profiles leak reusable hashes.
- In AD, the key is chaining relay, DNS, tickets and cached credentials.

## Mitigation and detection

- Update RoundCube and escape message bodies.
- Restrict PostgreSQL superuser and `COPY PROGRAM`.
- Sign LDAP/SMB, disable NTLM and protect ADIDNS.
- Audit tasks, DPAPI, GPO, UPN and SSSD cache; rotate credentials.

## References

- [0xdf — DarkCorp](https://0xdf.gitlab.io/2025/10/18/htb-darkcorp.html)
- [IppSec — DarkCorp](https://www.youtube.com/watch?v=miOE_yYh1JY)
- [Hack The Box — DarkCorp](https://app.hackthebox.com/machines/darkcorp)
