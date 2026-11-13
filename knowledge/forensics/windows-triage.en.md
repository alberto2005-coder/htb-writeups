---
topic: Windows forensic triage
tags: [forensics, windows, mft, usn, shellbags, evtx, usb, jscript]
---

# Windows forensic triage

**English** | [🇪🇸 Español](windows-triage.md)

## Concept

Windows triage combines file-system, execution, registry and device artefacts to reconstruct an intrusion. `$MFT`, `$UsnJrnl`, Prefetch, EVTX, ShellBags and USB records answer what ran, when and from where.

## When it applies

- A forensic image of a compromised endpoint.
- Execution of an archive or script.
- Persistence and lateral movement.
- Correlating events and user activity.

## Procedure

1. Document the time zone and evidence hashes.
2. Build a timeline with MFT, USN and Prefetch.
3. Review Security, System, PowerShell and Sysmon EVTX.
4. Analyse ShellBags, LNK files and USB records.
5. Correlate processes, files and accounts.

```powershell
MFTECmd.exe -f "$MFT" --csv out --csvf mft.csv
MFTECmd.exe -f "$UsnJrnl" --csv out --csvf usn.csv
PECmd.exe -d C:\Windows\Prefetch --csv out --csvf prefetch.csv
EvtxECmd.exe -d Logs --csv out --csvf evtx.csv
```

## Variants

- Execution through `wscript`/`cscript` and JScript.
- An archive containing an LNK or shortcut.
- USB as the source or exfiltration path.
- Persistence in tasks, services or WMI.

## Limitations

- Timestamps can be manipulated.
- Prefetch may be disabled.
- Logs may rotate or be missing.
- ShellBags do not always record the full path.

## Mitigation and detection

- Enable auditing and Sysmon with process telemetry.
- Centralise EVTX and protect the logs.
- Restrict script execution and USB devices.
- Alert on `wscript`, LNK, abnormal USN and service creation.

## References

- <https://ericzimmerman.github.io/>
- <https://attack.mitre.org/techniques/T1059/007/>
- <https://www.sans.org/white-papers/forensic-suite/>
