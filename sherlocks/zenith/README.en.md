---
sherlock: Zenith
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, phishing, evtx, persistence, privilege-escalation]
---

# Zenith — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

An email with a malicious attachment starts an intrusion on a Windows host. The analyst must identify initial execution, persistence and privilege escalation from system events.

## Evidence

- Email message and attachment.
- Security, System and PowerShell EVTX logs.
- Prefetch and process tree.
- Scheduled tasks and persistence keys.

```bash
sha256sum <EVIDENCE>.zip
7z l <EVIDENCE>.zip
```

## Investigation

### 1. Email and initial execution

Headers, attachment and filename are reviewed. The process-creation event shows the real parent: Outlook, an archiver or Explorer. That relationship separates phishing execution from a manual run.

```bash
EvtxECmd.exe -d Logs --csv out --csvf evtx.csv
```

### 2. Persistence

`Run` keys, scheduled tasks and services created after first access are located. Event time is compared with file time and prefetch.

- Task or service name.
- User who created it.
- Associated binary or script.
- First and last execution.

### 3. Privilege escalation

Events 4672 and 4688, plus PowerShell logs, reconstruct which account obtained privileges and with which tool. `lsass` access and local group changes are also reviewed.

## Conclusions

- Initial vector and executed file.
- Persistence mechanism and account used.
- Evidence of escalation.
- IOCs: paths, names and hashes, redacted.

## Lessons

- The parent process is more reliable than the executable name.
- A scheduled task can be missed if only `Run` keys are reviewed.
- PowerShell events must be correlated with the process tree.

## References

- <https://www.hackthebox.com/sherlocks/Zenith>
- <https://attack.mitre.org/techniques/T1566/001/>
- <https://attack.mitre.org/techniques/T1053/005/>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4688>
