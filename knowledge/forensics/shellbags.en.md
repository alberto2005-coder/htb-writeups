---
topic: Shellbags en Windows
tags: [forensics, windows, shellbags, usrclass, registry]
---

# Windows Shellbags

**English** | [🇪🇸 Español](shellbags.md)

## Concept

Shellbags record folders the user opened in Explorer, including network paths and removable drives. They live in `UsrClass.dat` and `NTUSER.DAT` and survive folder deletion.

## When it applies

- Reconstructing directory navigation.
- Confirming access to a USB drive or UNC share.
- Correlating with USBSTOR, MFT and LNK.

## Procedure

1. Copy `UsrClass.dat` and `NTUSER.DAT` from each profile.
2. Process them with `SBECmd`.
3. Filter by path, volume and time.
4. Cross-check with USB and MFT.
5. Document the path and timestamp.

```bash
SBECmd.exe -d evidence/Users --csv shellbags
```

## Variants

- BagMRU/Bags in `NTUSER.DAT`.
- Network paths and MTP devices.
- Per-application shellbags (Office, browsers).

## Limitations

- They do not prove a file was copied.
- Dates may reflect first or last visit.
- Profiles without `UsrClass.dat` provide nothing.

## Mitigation

- Clear history when unmounting media.
- Restrict network resource access.
- Audit removable-device use.

## Detection

- Paths to unauthorised drives.
- Access to `\host\share` from workstations.
- Correlation with USB events.

## References

- <https://github.com/EricZimmerman/SBECmd>
- <https://attack.mitre.org/techniques/T1059/>
- <https://www.hackthebox.com/sherlocks>
