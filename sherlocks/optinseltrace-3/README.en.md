---
sherlock: OpTinselTrace-3
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, memory, volatility3, powershell, defender, procdump]
---

# OpTinselTrace-3 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological note; no literal answers.

## Scenario

The security team captures a memory dump from a TinkerTech workstation (`santaclaus.bin`). The chain follows OpTinselTrace-2: the attacker used AWS access to deliver a file to an internal user. Identify the delivered file, the obfuscated script, the final binary and the Defender exclusion.

## Evidence

- `santaclaus.bin`, a Windows memory dump.
- Volatility 3 Windows profile.
- Files and EVTX recoverable from the dump.
- PowerShell and Defender indicators.

```bash
python3 vol.py -f santaclaus.bin windows.info
python3 vol.py -f santaclaus.bin windows.filescan > files.txt
```

## Investigation

### 1. Inventory and triage

Locate the user profile and recent files:

```bash
grep -i 'santaclaus' files.txt | head -40
python3 vol.py -f santaclaus.bin windows.filescan | grep -iE 'present|\.zip|\.lnk|\.exe'
```

The dump retains a ZIP and a shortcut (`click_for_present.lnk`) pointing to the lure.

### 2. Timeline

- ZIP download and LNK creation.
- LNK execution and PowerShell script.
- Concatenation obfuscation and `GRINCH`/`WrapPresent`.
- `present.exe` download and execution.
- Defender exclusion and `procdump`.

```bash
python3 vol.py -f santaclaus.bin windows.dumpfiles --virtaddr <ADDR>
python3 vol.py -f santaclaus.bin windows.filescan | grep -i evtx
```

### 3. Key artefact

The LNK runs a script that rebuilds strings and downloads the next stage. `present.exe` contains the C2 IP/port; `strings` can reveal the IP and IDA/Ghidra the port. PowerShell EVTX shows `Add-MpPreference` with a folder exclusion and the execution of `PresentForNaughtyChild.exe`.

```text
ZIP -> LNK -> obfuscated PowerShell -> present.exe -> Defender exclusion -> procdump
```

## Findings

- The attacker delivered a ZIP with an LNK and an obfuscated script.
- The script downloaded and ran a binary with C2.
- A Defender exclusion was added for evasion.
- IOCs are the ZIP/LNK/script/EXE names and hashes, IP/port and excluded path.

## Lessons

- LNK files inside ZIPs are a classic execution vector.
- Concatenation obfuscation is reversible with CyberChef/PSDecode.
- Memory retains scripts and binaries no longer on disk.
- `Add-MpPreference` is a detectable evasion technique.

## References

- <https://mwalkowski.com/post/sherlock-optinseltrace-3>
- <https://volatility3.readthedocs.io/>
- <https://attack.mitre.org/techniques/T1562/001/>
