---
sherlock: Heartbreaker-Continuum
domain: Malware Analysis
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [malware, powershell, pe, packer, sftp, exfiltration]
---

# Heartbreaker-Continuum — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal platform answers.

## Scenario

A romance-themed phishing campaign delivers an executable disguised as a TIFF image. The user opens it and the program shows a photo while, behind the scenes, it collects documents and sends them over SFTP. The evidence is a single binary; the job is to extract its logic and the credentials it uses.

## Evidence

```text
Heartbreaker-Continuum/Superstar_MemberCard.tiff.exe      binary delivered by email
```

```bash
sha256sum Superstar_MemberCard.tiff.exe
file Superstar_MemberCard.tiff.exe
```

## Investigation

### 1. Inventory and triage

A single 32-bit PE. Start static: `file`, `pefile`/PEStudio for headers, sections and timestamp; then `strings` in ASCII and UTF-16. The double extension already says the image is a decoy.

```bash
python3 -c "import pefile;pe=pefile.PE('Superstar_MemberCard.tiff.exe');print(hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint), pe.FILE_HEADER.TimeDateStamp)"
strings -n 6 Superstar_MemberCard.tiff.exe | head -40
strings -el Superstar_MemberCard.tiff.exe | grep -iE 'http|sftp|password|powershell' | head
```

### 2. Timeline

The PE `TimeDateStamp` and the embedded script's compile time are consistent with the campaign. There are no execution artefacts in the package, so the timeline is rebuilt from the binary itself: it runs, shows the image, profiles the host and copies files.

### 3. Key artefact

The binary is a **compiled PowerShell script**: it holds a reversed base64 string that, once decoded, reveals the script. There are the paths it copies (Documents, PDFs, mail), the staging folder `C:\Users\Public\HelpDesk-Tools`, the download of a portable WinSCP and the SFTP credentials.

```bash
# extract the blob and decode: reverse the string, then base64
python3 - <<'PY'
import base64
blob = open('blob.b64','rb').read().strip()
print(base64.b64decode(blob[::-1]).decode('utf-16-le', 'replace'))
PY
```

## Conclusions

- Delivery: romance-themed phishing with a double-extension `.tiff.exe`.
- Execution: compiled PowerShell showing a decoy and working in the background.
- Action: collection of documents and mail, compression and SFTP exfiltration with portable WinSCP.
- IOCs: binary hash, `HelpDesk-Tools` folder, SFTP server name and the account used.
- Persistence: none documented in the binary.

## Lessons

- An `.exe` named like an image is not an image: double extensions still work.
- "Compiled PowerShell" is not a native binary: the script is inside and comes back by reversing and decoding.
- Exfiltration credentials usually sit in the malware itself; extracting them lets you hunt the destination in the proxy.
- Mitigation: block executables from user folders, remove the double-extension association and apply ASR rules.
- Detection: `4688` with `powershell.exe` from `%TEMP%`, creation of `C:\Users\Public\HelpDesk-Tools`, portable `WinSCP.exe` execution and outbound SFTP.
- What is missing: a capture or proxy logs to confirm the upload.

MITRE: T1204.002 (malicious file), T1059.001 (PowerShell), T1074.001 (local data staging), T1048.002 (exfiltration over asymmetric encrypted channel).
