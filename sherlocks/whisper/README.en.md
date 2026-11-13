---
sherlock: Whisper
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, windows, registry, mft, mimikatz, shellbags, sam]
---

# Whisper — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A Windows endpoint shows signs of unauthorized access and credential theft. A forensic collection is provided to identify tool execution, downloaded files and browsing artefacts.

## Evidence

- `SYSTEM`, `SOFTWARE`, `SAM` and `NTUSER.DAT` hives.
- `$MFT` and `$UsnJrnl`.
- Prefetch.
- Microsoft Edge history and downloads.
- ShellBags and LNK files.

```bash
sha256sum <EVIDENCE>.zip
7z l <EVIDENCE>.zip
```

## Investigation

### 1. Inventory and triage

The user profile, time zone and window of interest are identified. Hives are loaded into analysis tools and a timeline is built from MFT and USN.

```bash
RegistryExplorer.exe
MFTECmd.exe -f "$MFT" --csv out --csvf mft.csv
```

### 2. Execution and download

Prefetch confirms execution of `mimikatz` and remote-access utilities. Edge history and the `Downloads` folder show where the files came from.

- Executable name and path.
- First and last access.
- Download URL and original filename.
- Temporal relation with files created in `Temp`.

### 3. Credential access and browsing

Mimikatz execution is correlated with access to the `lsass` process. ShellBags and LNK files reveal folders and files opened, even after deletion. The `SAM` hive is reviewed for local accounts and recent changes.

## Conclusions

- Tool executed and the user who launched it.
- Downloaded files and their origin.
- Evidence of credential access.
- IOCs: paths, names and hashes, redacted.

## Lessons

- Prefetch and USN complement each other: one confirms execution, the other file order.
- ShellBags survive deletion of the content.
- `lsass` access must be correlated with permissions and the binary used.

## References

- <https://www.hackthebox.com/sherlocks/Whisper>
- <https://attack.mitre.org/techniques/T1003/001/>
- <https://ericzimmerman.github.io/>
- <https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocess>
