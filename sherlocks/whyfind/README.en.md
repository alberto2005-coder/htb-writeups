---
sherlock: WhyFind
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, kape, registry, mft, browser, virtual-machine]
---

# WhyFind — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A Windows host shows activity the user does not recognise. A KAPE triage output is provided to reconstruct what ran, what was downloaded and whether a virtual machine was created to hide activity.

## Evidence

- KAPE output with `SYSTEM`, `SOFTWARE`, `NTUSER.DAT` and `UsrClass.dat` hives.
- `$MFT` and `$UsnJrnl` from the system volume.
- Browser history and downloads.
- Virtualisation and recent-execution artefacts.

```bash
sha256sum *.zip
7z l <EVIDENCE>.zip
```

## Investigation

### 1. Inventory and triage

Identify the host, timezone and time range. KAPE usually separates `C\` and `Registry`; both should be processed into a common timeline.

```bash
EvtxECmd.exe -d C:\Windows\System32\winevt\Logs --csv out --csvf security.csv
MFTECmd.exe -f "$MFT" --csv out --csvf mft.csv
```

Execution artefacts are sorted by time and correlated with network events.

### 2. Timeline

- Profile creation and modification.
- First and last access to downloaded files.
- Installers and binaries run from user paths.
- Appearance of virtual disks or devices.

`$MFT` and EVTX timestamps may differ; record the source and timezone.

### 3. Key artefact

Traces of a virtual machine in `NTUSER.DAT`, `UsrClass.dat` and Explorer recent items explain the activity the user did not recognise. Virtual disk names and installer paths reconstruct the order.

## Conclusions

- Which user started the activity and from which session.
- What software was installed and which files were opened.
- Which artefacts prove the VM was created.
- IOCs: paths, executable names and hashes, redacted.

## Lessons

- KAPE does not replace analysis: hives, MFT and browser data must be correlated.
- Virtualisation artefacts are easy to overlook.
- A timeline without a documented timezone produces false conclusions.

## References

- <https://www.hackthebox.com/sherlocks/WhyFind>
- <https://ericzimmerman.github.io/>
- <https://attack.mitre.org/techniques/T1564/001/>
