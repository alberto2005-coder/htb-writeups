---
sherlock: Nuts
difficulty: Medium
category: DFIR
platform: Hack The Box
state: Unverified
tags: [dfir, windows, nuget, supply-chain, powershell, defender, prefetch]
---

# Nuts — Hack The Box Sherlock

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Pending confirmation on HTB without a session; reference writeup, not played.
> No flags, hashes or real domains.

## TL;DR

The case centres on a Windows host with over 300,000 files and a malicious NuGet package. The package mimics a legitimate name (`PublishIgnor` versus `PublishIgnore`) and runs `init.ps1` during restore. The script downloads a payload, creates persistence and tampers with Defender. Evidence is spread across the `.nuget` cache, PowerShell history, Prefetch, scheduled tasks and antivirus events.

## Starting point

```powershell
Get-ChildItem C:\Users -Directory
Get-ChildItem C:\Users\<USER>\.nuget\packages -Directory | Measure-Object
Get-ChildItem C:\Users\<USER>\.nuget\packages -Directory | Where-Object Name -match 'publish'
```

With hundreds of thousands of paths, do not run a global `Get-ChildItem -Recurse`. Scope by user, date and extension. `Everything` or `rg` on specific paths beats recursive PowerShell.

## 1. The NuGet package

```powershell
Get-ChildItem C:\Users\<USER>\.nuget\packages\publishignor -Recurse |
  Select-Object FullName,Length,LastWriteTime
Get-Content C:\Users\<USER>\.nuget\packages\publishignor\<VERSION>\tools\init.ps1
```

Red flags:

- Name one letter off the legitimate package (typosquatting).
- Very recent version and a different publisher.
- `init.ps1`, `install.ps1` or `tools/` with download and execution.
- Obfuscated download URL, `Invoke-WebRequest`, `FromBase64String` or `iex`.
- A `.nupkg` with the same hash on other hosts.

Preserve the script as evidence and extract URLs as `<C2_HOST>`.

## 2. PowerShell history

```powershell
Get-Content C:\Users\<USER>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

Look for:

```text
dotnet add package PublishIgnor
Install-Package PublishIgnor
nuget install PublishIgnor
```

History confirms the user installed the package and where. It may also show the persistence commands run afterwards.

## 3. Prefetch and execution

```powershell
PECmd.exe -d C:\Windows\Prefetch --csv C:\Out --csvf prefetch.csv
```

Review `powershell.exe`, `cmd.exe`, `schtasks.exe`, `certutil.exe` and the payload name. Prefetch gives first/last run, count and opened files; it does not prove intent alone, but it frames the window.

## 4. Persistence

```powershell
Get-ScheduledTask | Where-Object TaskPath -notlike '\Microsoft\*' |
  Select-Object TaskName,TaskPath,State
Get-ChildItem C:\Windows\System32\Tasks -Recurse | Select-String '<C2_HOST>'
```

- Tasks outside `\Microsoft\` with an executable in `AppData`/`Temp`.
- Run keys (`HKCU\...\Run`, `HKLM\...\Run`).
- New services (7045) and `ImagePath` changes.
- `init.ps1` may create the task with `schtasks /create` or `Register-ScheduledTask`.

## 5. Defender

```powershell
Get-MpPreference | Select-Object ExclusionPath,ExclusionProcess
Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' |
  Where-Object Id -in 1116,1117,5001,5007
```

- Exclusions added during the incident window.
- 1116/1117 detections with the payload name.
- 5001/5007 show protection was disabled or configuration changed.
- Check whether the attacker ran `MpCmdRun.exe` or `Set-MpPreference`.

## 6. Timeline

| Time (UTC) | Event |
|---|---|
| T0 | `dotnet add package PublishIgnor` |
| T0+1m | `init.ps1` runs during restore |
| T0+2m | Payload download |
| T0+3m | Scheduled task created |
| T0+4m | Defender exclusion added |
| T0+5m | First beacon |

## Lessons learned

- A NuGet typosquat runs with the privileges of the user restoring the package.
- `init.ps1` is the entry point; the `.nupkg` is the evidence to preserve.
- In a huge tree, scope by user and name instead of walking everything.
- Prefetch, tasks and Defender correlate; none is enough alone.
- Supply chain needs no exploit: the user installs the package.

## Mitigations and detection

- Use private feeds and verify package ownership; block look-alike names.
- Review `init.ps1`/`install.ps1` before restore and disable scripts where possible.
- Alert on tasks outside `\Microsoft\`, Defender exclusions and `schtasks` from PowerShell.
- Detection: suspicious package installs, `init.ps1` with downloads, 1116/1117 and 5007.
- Isolate the host, revoke tokens and rebuild the NuGet cache.

MITRE: T1195.002, T1059.001, T1053.005, T1562.001.

## References

- <https://mwalkowski.com/post/sherlock-nuts>
- <https://attack.mitre.org/techniques/T1195/002/>
- <https://learn.microsoft.com/en-us/nuget/concepts/package-installation>
