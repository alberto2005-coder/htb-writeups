---
sherlock: Mysterious
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, scheduled-tasks, usb, lnk, registry]
---

# Mysterious — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original evidence or literal answers.

## TL;DR

A user runs a file from a removable device, leaving traces in USBSTOR, LNK, prefetch and scheduled tasks. The execution sequence and the file's origin are reconstructed.

## Scenario

A host shows activity the user cannot explain. The `SYSTEM` hive, the user profile and execution artefacts are provided to determine what was connected, what was opened and what persisted.

## Artefacts

- `SYSTEM` (USBSTOR, MountedDevices).
- `NTUSER.DAT` (RecentDocs, UserAssist, RunMRU).
- LNK, jumplists and prefetch.
- Scheduled tasks and EVTX.

## Methodology

1. Identify USB devices by serial and volume.
2. Review LNK/jumplists for files opened from the device.
3. Confirm execution with prefetch/UserAssist.
4. Look for tasks or keys created after the connection.
5. Build the timeline and document the user.

```bash
reg query HKLM\\SYSTEM\\CurrentControlSet\\Enum\\USBSTOR /s
JLECmd.exe -d C:\\Evidence\\jumplist --csv C:\\Evidence\\out
PECmd.exe -d C:\\Evidence\\prefetch --csv C:\\Evidence\\pf
```

## Sample questions

- Which USB device was connected and when?
- Which file was opened from it?
- Which user executed the file?
- Was persistence created afterwards?
- Were traces deleted?

## Tools

`Registry Explorer`, `JLECmd`, `LECmd`, `PECmd`, `Timeline Explorer`.

## Evidence and redaction

Screenshots of keys and the timeline are kept with serials, users and paths redacted.

## Lessons learned

- USBSTOR correlates device, serial and first connections.
- LNK and jumplists reveal files opened from removable media.
- UserAssist/prefetch confirm execution.
- Persistence may be created minutes later.

## Detection

- Alert on executables run from removable drives.
- Monitor task creation after USB connections.
- Correlate 4688 with USBSTOR.
- Block execution from removable media.

## References

- <https://app.hackthebox.com/sherlocks/Mysterious>
- <https://attack.mitre.org/techniques/T1091/>
- <https://attack.mitre.org/techniques/T1053/005/>
