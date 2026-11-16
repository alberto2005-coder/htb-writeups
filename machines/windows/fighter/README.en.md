---
machine: Fighter
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, iis, sqli, xp-cmdshell, applocker, msbuild, capcom, privesc]
---

# Fighter — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The IIS site has a stacked SQL injection that enables `xp_cmdshell` and runs commands as `sqlserv`; a PowerShell reverse shell provides access. `clean.bat`, run by a `decoder` scheduled task, is writable: truncate and rewrite it to get that account. The loaded `Capcom.sys` driver allows kernel-mode code execution and SYSTEM. As an alternative, AppLocker can be bypassed with `MSBuild.exe` and a `UsingTask` XML.

## Recon

```bash
nmap -Pn -sCV -p80 <IP>
```

- `80` IIS 8.5 with a Street Fighter themed site and several vhosts.
- MSSQL 2014 sits behind the web app; SMB and RDP are not exposed.
- Windows Server 2012 R2, with no useful missing hotfix.

## Enumeration

`wfuzz` finds vhosts and `feroxbuster` maps application paths. The login form is SQL injectable; a stacked query runs `EXEC xp_cmdshell 'whoami'` and confirms the database runs as `sqlserv`.

## Foothold

The stacked SQL injection enables `xp_cmdshell`; it launches PowerShell to obtain a reverse shell as `sqlserv`. In Beyond Root, AppLocker is bypassed with `MSBuild.exe`, a trusted executable that compiles a `UsingTask` with `TaskFactory="CodeTaskFactory"` and runs C# in memory. The variant is:

```powershell
C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe sc.xml
```

## Lateral movement

`C:\users\decoder\clean.bat` grants modify rights to `Everyone`. It cannot be overwritten directly, but `cmd /c copy /y NUL clean.bat` empties it and the payload can then be appended. `decoder`'s scheduled task runs it, yielding a shell as that user.

## Privilege escalation

`driverquery /v` shows `Capcom.sys`, a signed vulnerable driver that allows writing to kernel memory from user mode. A public exploit disables the protections and runs a SYSTEM shell.

```powershell
driverquery /v | findstr /iv "system32\\drivers"
sc.exe query capcom
```

## Evidence

- `xp_cmdshell` running `whoami` as `sqlserv`.
- `MSBuild.exe` with the task XML as an alternative bypass.
- `clean.bat` truncated and rewritten.
- `Capcom.sys` driver and a SYSTEM shell.

## Lessons learned

- Path- and extension-based AppLocker lets signed binaries through.
- Scheduled scripts with broad permissions are a user hop.
- A signed vulnerable driver completely breaks the kernel/user boundary.
- Enumerating drivers matters as much as enumerating services.

## Mitigation and detection

- Parameterise queries and disable `xp_cmdshell`.
- Enforce AppLocker/WDAC publisher rules and block MSBuild for non-developers.
- Tighten ACLs on scripts run by scheduled tasks.
- Enable HVCI and block known vulnerable drivers (Capcom.sys).

## References

- [0xdf — Fighter](https://0xdf.gitlab.io/2022/04/25/htb-fighter.html)
- [IppSec — Fighter](https://www.youtube.com/watch?v=CW4mI5BkP9E)
- [Hack The Box — Fighter](https://app.hackthebox.com/machines/fighter)
