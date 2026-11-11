---
sherlock: TickTock
domain: DFIR / Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, mft, teamviewer, powershell, evtx, timestomp, merlin]
---

# TickTock — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired according to the public writeup and its difficulty tag; not verified with an HTB session.
> Method note; no literal answers, IOCs or real credentials.

## Scenario

Gladys, a new employee, receives an email from the fake IT team and calls to allow remote access. The "IT" team is a group of attackers. A triage of roughly 990 files from her workstation is provided: MFT, TeamViewer logs, EVTX, Prefetch, copies of `C:\Windows` and Defender logs. Reconstruct access, execution, clock manipulation and exfiltration.

## Evidence

- `$MFT` or its export.
- `C/Users/gladys/AppData/Local/TeamViewer/TeamViewer15_Logfile.log`.
- PowerShell, Security and System EVTX.
- `C/Windows/Prefetch` and `C/Windows/System32` (including event logs).
- `C/ProgramData/Microsoft/Windows Defender/Support/MPLog-*.log`.
- Files on the user's desktop.

```bash
find Collection -maxdepth 3 -type f | wc -l
sha256sum Collection/C/Users/gladys/AppData/Local/TeamViewer/TeamViewer15_Logfile.log
```

## Investigation

### 1. MFT: what was on the desktop

```bash
MFTECmd.exe -f 'Collection/C/$MFT' --csv out/ --csvf mft.csv
```

In Timeline Explorer, filter by `ParentPath` for Gladys's desktop. Two files should not be there: a C2 agent (`merlin.exe`, an open-source Go agent) and a time-manipulation script (`Invoke-TimeWizard.ps1`). The MFT also gives path, size and timestamps; if the binary is resident, it can be read from the record itself.

### 2. TeamViewer: access and session

```bash
grep -iE 'session|connect|start|file|transfer' \
  Collection/C/Users/gladys/AppData/Local/TeamViewer/TeamViewer15_Logfile.log | head -40
```

The log shows the incoming session, the name the attacker used, the start time and the agent transfer. It proves initial access, before any execution. The session and name are redacted here as `<SESSION_ID>` and `<ATTACKER_NAME>`.

### 3. PowerShell and the clock

```bash
chainsaw search --skip-errors 'powershell' Collection/C/Windows/ \
  --timestamp 'Event.System.TimeCreated_attributes.SystemTime' \
  --from '2023-05-04T11:35:00'
```

Look for the command that changes the clock or configures BitLocker. Base64-obfuscated commands decode with CyberChef or `base64 -d`; the content usually includes the BitLocker password (`<BITLOCKER_PASS>`) and calls to `Set-Date`/`Set-TimeZone`. `Invoke-TimeWizard.ps1` confirms the intent.

### 4. Defender and execution

```bash
strings -e l 'Collection/C/ProgramData/Microsoft/Windows Defender/Support/MPLog-07102015-052145.log' \
  | grep -i 'merlin.exe'
```

`MPLog` keeps the category assigned to the agent and its hashes (`<SHA1>`/`<SHA256>`), even though the file has an old date: the attacker moved the clock so the record would look old. The date in the name is not the real execution date.

```bash
EvtxECmd.exe -f 'Collection/C/Windows/System32/winevt/Logs/Security.evtx' \
  --csv out/ --csvf security.csv
```

In Security, filter event **4616** (time change). Separate changes by `SystemSettingsAdminFlows.exe` (the Windows UI) from the script's changes; `SubjectUserSid` and the process attribute them.

### 5. Timeline

| Time | Source | Event |
|---|---|---|
| 11:35 | TeamViewer | incoming session starts |
| + minutes | MFT | `merlin.exe` and `Invoke-TimeWizard.ps1` appear |
| later | PowerShell/EVTX | time/BitLocker commands and agent execution |
| later | Defender | agent detection/category |
| at the end | Security 4616 | multiple time changes attributable to the script |

EVTX and MFT times must be read in UTC; the manipulated clock affects system timestamps, not the SIEM's receipt time.

## Conclusions

- Initial access was **TeamViewer**, not an exploit: social engineering with legitimate remote access.
- The attacker left a C2 agent and a time-manipulation script; the goal was to break the timeline and probably BitLocker.
- MFT and the TeamViewer log prove delivery; Defender and EVTX prove execution.
- Event 4616 is the evidence of clock manipulation, but legitimate system changes must be separated.
- The session, name, password, hashes and C2 IP are not published.

## Lessons

- Legitimate remote access can be the foothold; TeamViewer telemetry matters as much as PowerShell.
- The MFT reconstructs delivery even if the binary is deleted; name and path remain.
- Base64 is not encryption: decoding the command reveals intent and secrets.
- An old-dated `MPLog` may be a **timestomping** clue, not an old record.
- MITRE: T1219 (remote access software), T1059.001 (PowerShell), T1070.006 (timestomp), T1027 (obfuscation), T1562.001 (impair defenses).
- Mitigation: restrict TeamViewer to authorised hosts and users, enable 4616 and script block logging, and correlate MFT/EVTX/Defender.

## References

- <https://mwalkowski.com/post/sherlock-ticktock/>
- <https://app.hackthebox.com/sherlocks/TickTock>
