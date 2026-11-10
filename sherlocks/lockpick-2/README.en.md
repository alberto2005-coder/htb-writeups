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
- `malware.zip` holding the binary: an ELF named `update`, **UPX-packed**.
- The encrypted documents (`expanding-horizons.pdf`, `takeover.docx`) and the `countdown.txt` note.

## Method

1. **Ransom note**: extension of the encrypted files, amount and payment address, contact. It is the IOC source.

2. **Sample**: check packing first.

```bash
upx -d sample -o sample.unpacked   # if packed
detect-it-easy sample
```

3. **Algorithm**: `upx -d update`, then `encrypt_file` shows `aes_256_cbc`. The key and IV are **inside the binary** (32 and 16 bytes, hex), so the decryption material comes from the disassembly, not the network.

4. **Decrypt**: AES-256-CBC with that key and IV over the files in `share`; validate by opening the resulting PDF and DOCX (`Australian market`, `Notionwide Bank`).

5. **Report**: affected files, extension, key, encryption window and the ransom demanded (one million pounds in `countdown.txt`). The key file's name comes from the note's short URL.

Difficulty note: public indexes list this as Easy while one writeup tags it Hard; it is left as **Easy** and the discrepancy is recorded.

## What it teaches

- The ransom note is evidence: it identifies the family and the infrastructure.
- UPX is detected and reversed in one command; it is not real protection.
- Recovering without paying requires understanding the key scheme, not just the algorithm.

## Pitfalls

- **`DANGER.txt`**: it holds the ZIP password; without reading it there is no sample.
- **Block encryption**: large files may be encrypted in chunks with a per-block IV.
- **Encoding is not encryption**: base64/XOR protect nothing; AES with an asymmetric key does.
