---
sherlock: Lockpick
domain: Malware analysis
difficulty: Easy
platform: Hack The Box
evidence: Ransomware sample and encrypted files
tools: [Detect It Easy, Ghidra, x64dbg, CyberChef]
---

# Lockpick — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

First case in the **Lockpick** family: ransomware has encrypted company data. You must analyse the sample to understand how it encrypts, which key it uses and how to recover the files without paying.

## Evidence

- The binary sample plus a set of encrypted files and the ransom note.

## Method

1. **Triage**: hash, file type, compiler, packing.

```bash
sha256sum sample; file sample
detect-it-easy sample
strings -n 8 sample | head -50
```

2. **Imports**: look for `CryptAcquireContext`/`CryptEncrypt` (CryptoAPI), `BCrypt*`, or embedded AES/RSA. A Go or .NET binary changes the analysis approach.

3. **Key**: find how it is generated or derived. Typically AES with a random per-file key, that key then encrypted with an RSA public key; when the symmetric key is embedded or obfuscated, extract it.

4. **Decrypt**: reproduce the routine with the right algorithm and mode, and verify against the original file header.

```python
from Crypto.Cipher import AES
# key/IV recovered; mode and padding must match the binary
```

5. **Document** the IOCs and the exact code point where encryption happens.

## What it teaches

- Ransomware keeps its encryption logic in the binary: key, algorithm and format.
- `strings` plus imports solve half the triage without disassembly.
- Recovery works when the key is embedded, not when it is asymmetric and deleted.

## Pitfalls

- **Running the sample**: always an isolated VM with no network.
- **Mode and padding**: a different AES-CBC IV yields garbage; verify with the first block.
- **Packing**: if strings are noise, unpack (UPX or other) before analysing.
