---
sherlock: Lockpick 2.0
domain: Malware analysis
difficulty: Easy
platform: Hack The Box
evidence: Encrypted share and ransomware sample
tools: [UPX, Ghidra, CyberChef, Python]
---

# Lockpick 2.0 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

The same crew strikes again: a file share is encrypted and policy is **no negotiation**. You must recover the files by analysing the sample and the ransom note.

## Evidence

- `DANGER.txt` with the warning and the password for the sample ZIP.
- A `share` directory with the encrypted files and the attacker's note.
- `malware.zip` holding the binary.

## Method

1. **Ransom note**: extension of the encrypted files, amount and payment address, contact. It is the IOC source.

2. **Sample**: check packing first.

```bash
upx -d sample -o sample.unpacked   # if packed
detect-it-easy sample
```

3. **Algorithm**: identify AES/RSA and, above all, **where the key comes from**. This family usually encrypts with a key derived from local or embedded data.

4. **Decrypt**: rebuild the flow and test on a small file; validate against a known header (`PK`, `%PDF`, etc.).

5. **Report**: affected files, extension, key, encryption window and recommendations (offline backups, segmentation).

## What it teaches

- The ransom note is evidence: it identifies the family and the infrastructure.
- UPX is detected and reversed in one command; it is not real protection.
- Recovering without paying requires understanding the key scheme, not just the algorithm.

## Pitfalls

- **`DANGER.txt`**: it holds the ZIP password; without reading it there is no sample.
- **Block encryption**: large files may be encrypted in chunks with a per-block IV.
- **Encoding is not encryption**: base64/XOR protect nothing; AES with an asymmetric key does.
