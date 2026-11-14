---
sherlock: Baggage
category: DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, shellbags, kape, usb]
---

# Baggage — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

An employee connects removable devices and opens folders outside their profile. A KAPE collection from a Windows host is provided, and the task is to reconstruct which folders and drives were visited.

## Evidence

- `UsrClass.dat` and `NTUSER.DAT` for each profile.
- `$MFT`, `$J` and USB device records.
- KAPE output with the directory structure.

```bash
sha256sum -c hashes.txt
tree -L 3 evidence | head -60
```

## Investigation

### 1. Inventory and scope

Identify profiles and separate user artefacts from system artefacts. Record paths and timestamps before running tools.

```bash
find evidence -iname 'UsrClass.dat' -o -iname 'NTUSER.DAT'
```

### 2. Shellbags

`SBECmd` processes `UsrClass.dat` and shows opened folders, including network paths and removable drives. Correlate with `USBSTOR` and `$MFT` to distinguish actual access from a mere entry.

```bash
SBECmd.exe -d evidence/Users --csv shellbags
```

### 3. Timeline

Compare shellbag times with USB connection and created files. The sequence shows which folder was opened first and which drive was used.

## Conclusions

- Shellbags prove folder navigation, not just presence.
- USBSTOR and MFT confirm the removable drive.
- The timeline orders access and copying.

## Lessons

- `UsrClass.dat` preserves paths the user saw.
- KAPE speeds collection, but artefacts must be validated.
- A conclusion needs at least two sources.
- USB devices leave traces in several registries.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://github.com/EricZimmerman/SBECmd>
- <https://attack.mitre.org/techniques/T1059/>
