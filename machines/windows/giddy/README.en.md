---
machine: Giddy
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, iis, sqli, winrm, ntlm, unifi-video, privilege-escalation]
---

# Giddy — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An IIS application with SQLi leaks credentials and grants WinRM access. Local enumeration finds the UniFi Video service running as SYSTEM with a vulnerable version, allowing command execution with high privileges.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80,5985 <IP>
```

The site is an ASP.NET application. Enumerate paths and parameters with `feroxbuster`. Port 5985 (WinRM) is exposed.

## Initial access

The login form is injectable. Use `sqlmap` or a manual payload to extract users and hashes:

```bash
sqlmap -r login.txt --batch --dbs
```

Crack the hashes with `hashcat`/`john`. The credentials work over WinRM:

```bash
evil-winrm -i <IP> -u <user> -p '<password>'
```

If WinRM rejects the password directly, capture an NTLMv2 hash with `Responder` and crack it.

## Local enumeration

```powershell
whoami /priv
Get-Service
Get-Process
```

The UniFi Video service runs as SYSTEM and uses an old version with a command-execution vulnerability.

## Escalation to SYSTEM

Locate the service executable and version. Use a public UniFi Video exploit or replace a weakly permissioned binary/script. Execution happens as SYSTEM:

```powershell
.\exploit.exe
whoami
```

Read and redact the administrator flag.

## Evidence

- SQLi request and redacted dump.
- WinRM session.
- UniFi Video service and version.
- `whoami` as SYSTEM.

## Lessons learned

- IIS and ASP.NET still expose SQLi in legacy forms.
- WinRM enables lateral movement with valid credentials.
- Third-party services running as SYSTEM are escalation targets.
- NTLMv2 remains useful when the password is not reusable.

## Mitigation and detection

- Parameterised queries and a WAF.
- Restrict WinRM to administration.
- Update UniFi Video and run it under a low-privilege service account.
- Monitor process creation from services.

## References

- <https://www.hackthebox.com/machines/giddy>
- <https://owasp.org/www-community/attacks/SQL_Injection>
- <https://github.com/swisskyrepo/PayloadsAllTheThings>
