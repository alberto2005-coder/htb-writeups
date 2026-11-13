---
sherlock: RomCom
category: DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, cve-2025-8088, mft, usn-journal, usb]
---

# RomCom — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A Windows host is investigated after a seemingly harmless archive triggered execution and persistence. The analyst must reconstruct extraction, execution and the exact timeline.

## Evidence

- Forensic image of the system volume.
- `$MFT` and `$UsnJrnl`.
- Prefetch and execution artefacts.
- USB device records.
- Copy of the archive and the shortcut used.

```bash
sha256sum <EVIDENCE>.zip
```

## Investigation

### 1. Inventory and triage

The host time zone is documented and a timeline is built from MFT, USN and prefetch. Creation, modification and access times are treated as separate sources.

```bash
MFTECmd.exe -f "$MFT" --csv out --csvf mft.csv
PECmd.exe -d C:\Windows\Prefetch --csv out --csvf prefetch.csv
```

### 2. Extraction and execution

The archive name and extraction path are located. CVE-2025-8088 abuses a path inside an archive to write outside the intended destination. The result is usually a shortcut or executable placed in a startup path.

- Creation time of the extracted file.
- Real path versus the path shown by the archiver.
- First access and execution of the binary or LNK.
- Correlation with prefetch and USN.

### 3. Persistence and propagation

`Startup`, `Run`, scheduled tasks and USB device records are reviewed. A shortcut on a removable drive can execute on another host and explain propagation.

## Conclusions

- Archive and extraction path.
- Shortcut or binary created outside the expected directory.
- Execution confirmed by prefetch and USN.
- IOCs: names, paths and hashes, redacted.

## Lessons

- The path shown by an archiver is not necessarily the real on-disk path.
- `$UsnJrnl` provides creation and rename order that the MFT alone does not show.
- Shortcuts on USB drives are propagation vectors.

## References

- <https://www.hackthebox.com/sherlocks/RomCom>
- <https://nvd.nist.gov/vuln/detail/CVE-2025-8088>
- <https://attack.mitre.org/techniques/T1204/002/>
- <https://ericzimmerman.github.io/>
