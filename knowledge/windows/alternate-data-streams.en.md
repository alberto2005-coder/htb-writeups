---
topic: Alternate Data Streams (ADS)
tags: [windows, ntfs, ads, data-hiding, forensics, powershell]
---

# Alternate Data Streams (ADS)

**English** | [🇪🇸 Español](alternate-data-streams.md)

## Concept

NTFS allows extra data streams on a file using `file:stream:$DATA`. The main stream does not change size or content, so passwords, binaries or notes can be hidden in apparently normal files.

## When it applies

- NTFS volumes on Windows.
- Files shared over SMB.
- Applications storing metadata in streams.
- Hunting for hidden credentials or payloads.

## Procedure

1. List streams with `dir /r` or PowerShell.
2. Read the stream content.
3. Check whether the stream is executed or interpreted.
4. Extract the data for analysis.
5. Document path, name and size.

```powershell
Get-Item .\file.txt -Stream *
Get-Content .\file.txt -Stream Password
cmd /c dir /r
```

## Variants

- `:Password:$DATA` stream with a password.
- `:Zone.Identifier` stream recording download origin.
- Binary hidden in a stream and run with `wmic` or `rundll32`.
- Streams on directories and system files.

## Limitations

- Requires NTFS; FAT/exFAT does not support it.
- Copying the file elsewhere may lose streams.
- Some tools do not show ADS by default.
- Backups and antivirus may inspect them.

## Mitigation and detection

- Monitor stream creation and `:*:$DATA` access.
- Inspect streams during triage and downloads.
- Block execution from user paths.
- Alert on `dir /r`, `Get-Item -Stream` and processes reading streams.

## References

- <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-fscc/c54dec26-1551-4d3a-a0ea-4fa40f848eb3>
- <https://attack.mitre.org/techniques/T1564/004/>
- <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.management/get-item>
- <https://forensics.wiki/alternate_data_streams/>
