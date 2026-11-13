---
sherlock: Caught
category: DFIR
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [dfir, active-directory, jscript, sliver, gpo, wmi]
---

# Caught — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

An insider threat uses Active Directory to move laterally and maintain access. The analyst reconstructs the chain from JScript execution to WMI persistence and GPO abuse.

## Evidence

- Security, PowerShell and Sysmon logs.
- AD objects and ACL changes.
- JScript files and deserialization artefacts.
- GPO events and WMI consumers.
- Network telemetry consistent with Sliver.

```bash
sha256sum <EVIDENCE>.zip
7z l <EVIDENCE>.zip
```

## Investigation

### 1. Initial execution

`wscript`/`cscript`, command lines and scripts under user paths are identified. JScript deserialization can execute code without a conventional binary; created objects and the parent process are reviewed.

```powershell
Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-PowerShell/Operational'; ID=4104}
```

### 2. Movement and permissions

ACL changes are correlated with the `GenericAll` → `GenericWrite` → GPO abuse chain. The analyst documents which object gained control, over which target, and when.

- Modified user or group.
- Granted right.
- Linked GPO and affected computer.
- Password or group change.

### 3. Persistence and C2

WMI event consumers, scheduled tasks and services are reviewed. Network events and disk or memory artefacts are compared with the Sliver profile: beacon, sessions and tasks.

```powershell
Get-WmiObject -Namespace root\subscription -Class __EventConsumer
Get-WmiObject -Namespace root\subscription -Class __EventFilter
```

## Conclusions

- Script and user that started the chain.
- AD privilege path and abused GPO.
- WMI persistence and C2 evidence.
- IOCs: paths, accounts, GUIDs and hashes, redacted.

## Lessons

- A seemingly minor ACL change can enable full GPO abuse.
- WMI consumers are quiet, persistent mechanisms.
- JScript deserialization requires reviewing scripts, not just executables.

## References

- <https://www.hackthebox.com/sherlocks/Caught>
- <https://attack.mitre.org/techniques/T1053/005/>
- <https://attack.mitre.org/techniques/T1546/003/>
- <https://learn.microsoft.com/en-us/windows/win32/wmisdk/receiving-wmi-events>
