---
sherlock: Hat Trick
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, evtx, scheduled-tasks, credential-access, timeline]
---

# Hat Trick — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no original evidence or literal answers.

## TL;DR

Windows DFIR case focused on scheduled-task creation and credential access. EVTX, registry and MFT identify the binary, the persistent task, the account used and the incident time.

## Scenario

A host raises alerts for persistence and after-hours execution. A triage collection is provided; reconstruct the chain and impact.

## Artifacts

- Security/System/TaskScheduler EVTX.
- `SOFTWARE` and `NTUSER.DAT`.
- `C:\Windows\System32\Tasks`.
- Prefetch, Amcache and `$MFT`.

## Methodology

1. Review scheduled tasks and their history (106/200/201).
2. Identify binaries in user paths and confirm their creation.
3. Correlate 4624/4688 with task execution.
4. Review LSASS/SAM access and credential tools.
5. Document persistence and remove it during analysis.

```bash
schtasks /query /fo LIST /v
EvtxECmd.exe -d C:\Evidence\evtx --csv C:\Evidence\out
```

## Sample questions

- Which task was created and with what name?
- Which binary does it run and from which path?
- Which account created it?
- When did it first execute?
- Was there credential access?

## Tools

`EvtxECmd`, `Autoruns`, `Timeline Explorer`, `PECmd`, `MFTECmd`.

## Evidence and redaction

Screenshots of tasks and events are kept with users and paths redacted. No literal answers are published.

## Lessons learned

- Scheduled tasks are stealthy, common persistence.
- TaskScheduler history confirms execution.
- Binaries in `AppData`/`ProgramData` deserve review.
- Correlation with 4624 identifies the account.

## Detection

- Alert on tasks created outside the inventory.
- Monitor actions running scripts from user paths.
- Correlate 4698/106 with child processes.
- Review LSASS and SAM access.

## References

- <https://app.hackthebox.com/sherlocks/HatTrick>
- <https://attack.mitre.org/techniques/T1053/005/>
- <https://learn.microsoft.com/en-us/windows/security/threat-protection/auditing/event-4698>
