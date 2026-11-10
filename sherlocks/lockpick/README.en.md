---
sherlock: Lockpick
domain: Malware analysis
difficulty: Easy
platform: Hack The Box
evidence: Ransomware sample, encrypted files and ransom note
tools: [IDA, Ghidra, strings, CyberChef]
state: Retired
tags: [dfir, malware, ransomware, linux, static-analysis]
---

# Lockpick — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

Forela refuses to pay: part of its UNIX servers is encrypted and the files must be recovered by analysing the sample. The ZIP ships a `DANGER.txt` with the archive password and the warning to handle the binary only inside an isolated VM.

## Evidence

- `DANGER.txt` (ZIP password and warning).
- The ransomware binary, unpacked.
- A directory of encrypted files.

## Investigation

1. **Triage**: hash and type; this is a Linux ELF, not a PE.

```bash
md5sum lockpick; file lockpick; strings -n 8 lockpick | head -40
```

2. **Encryption flow**: in IDA/Ghidra, `main` walks a directory and calls `encrypt_file(path, key)`. The key is **embedded in the binary**, not negotiated with a server — which is why recovery is possible without paying.

3. **Key and algorithm**: the case question is literally the key string. Find it in the encryption routine (or via `strings` when it is not obfuscated) and confirm which function consumes it.

4. **Decrypt**: reproduce the inverse (AES in ECB/CBC depending on the disassembly) over a copy of the files and validate against a known header.

```python
from Crypto.Cipher import AES
# key recovered from the binary; mode and padding must match the sample's
```

5. **Integrity**: the case asks for the MD5 of one decrypted file (`complaints.csv` in public writeups) to prove the recovery is correct.

## Findings

- **ELF ransomware for UNIX** with a static symmetric key baked in.
- No C2 and no asymmetric material: the encryption is reversible from the sample.
- `DANGER.txt` is part of the chain of custody: archive password and isolation warning.

## Lessons

- `file` plus `strings` finish triage before the disassembler opens.
- A static key in the binary is the attacker's worst design: decryption automates.
- The recovered file's hash is the proof that the inverse is implemented correctly.

## Pitfalls

- **Running the sample**: isolated VM, no network, always.
- **Mode and padding**: a different IV or mode yields garbage; verify with the first block.
- **Cipher vs encoding**: this is real crypto with an embedded key, not base64.
