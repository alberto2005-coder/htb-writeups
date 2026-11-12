---
machine: StreamIO
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, sqli, mssql, lfi, rfi, bloodhound, laps, active-directory]
---

# StreamIO — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`watch.streamio.htb` has a SQLi that leaks hashes; the credentials grant panel access, whose `debug` parameter allows LFI and RFI. The chain continues with MSSQL, Firefox saved credentials, BloodHound and LAPS to the domain administrator.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80,443,445,1433,5985 <IP>
```

The TLS certificate reveals `watch.streamio.htb`. Add both vhosts to hosts. Enumerate paths and subdomains.

## Initial access

`search.php` is injectable in MSSQL. Extract users and hashes:

```bash
sqlmap -r search.txt --batch --dbms=mssql
hashcat -m 0 hashes.txt rockyou.txt
```

Cracked credentials log in at `streamio.htb/login.php`.

## LFI and RCE

The admin panel accepts `?debug=`. Use a PHP wrapper to read source code:

```bash
curl 'https://streamio.htb/admin/?debug=php://filter/convert.base64-encode/resource=index.php'
```

The source reveals `db_admin` credentials and an RFI-vulnerable `include`. Host a PHP file and include it for a shell.

## Lateral movement

```powershell
sqlcmd -S localhost -U db_admin -P '<password>'
```

Enumerate databases and extract a backup with another user's credentials. Access over WinRM. The Firefox profile holds saved credentials reused in the domain.

## Escalation to administrator

Run BloodHound and identify that the user can add themselves to a group with `ReadLAPSPassword`. Abuse it to read the domain controller's LAPS password:

```powershell
bloodyAD --host dc.streamio.htb -d streamio.htb -u <user> -p '<password>' add groupMember 'CORE STAFF' <user>
```

Use the LAPS password to access as administrator and read the flag.

## Evidence

- SQLi and redacted hashes.
- LFI with source code.
- MSSQL credentials and backup redacted.
- BloodHound and LAPS output redacted.

## Lessons learned

- A SQLi on a subdomain can compromise the whole domain.
- `debug` parameters and dynamic includes mean RCE.
- Browser credentials get reused.
- Misdelegated LAPS hands over the DC local password.

## Mitigation and detection

- Parameterise queries and limit SQL errors.
- Remove debug parameters in production.
- Restrict `include` to allowed paths.
- Audit LAPS delegation and privileged groups.

## References

- <https://www.hackthebox.com/machines/streamio>
- <https://bloodhound.readthedocs.io/>
- <https://learn.microsoft.com/en-us/windows-server/identity/laps/laps-overview>
