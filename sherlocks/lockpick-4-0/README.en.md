---
sherlock: Lockpick 4.0
category: Malware Analysis
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [malware-analysis, ransomware, reverse-engineering, c2, iocs]
---

# Lockpick 4.0 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

Forela.org suffers a ransomware attack. Users cannot open files and a ransom note appears. A malware sample and artifacts from one host are provided. Understand the encryption, extract configuration and document IOCs.

## Evidence

- Ransomware sample and ransom note.
- Memory dump or triage from the affected host.
- Encrypted files and changed extensions.

```bash
file sample.exe
sha256sum sample.exe
strings -el sample.exe | head
```

## Investigation

### 1. Inventory and triage

Isolate the sample, hash it and review imports, sections and signature. `PEStudio`, `capa` and `floss` identify capabilities and obfuscated strings. Preserve the ransom note as evidence.

```bash
capa -v sample.exe
floss sample.exe
```

### 2. Timeline

The binary enumerates drives, stops services and encrypts files by extension. Configuration includes the extension list, public key and payment panel URL. Correlate with host events to fix the order.

```bash
vol -f memory.raw windows.netscan
vol -f memory.raw windows.malfind
```

### 3. Key artifact

The initialization routine holds encrypted configuration. Deobfuscation reveals target extensions, mutex name and C2 domain. The symmetric key is protected with RSA; without the private key decryption is impossible, but configuration is enough to detect and contain.

## Conclusions

- The ransomware uses hybrid encryption and embedded configuration.
- The note and extension are high-confidence IOCs.
- C2 and payment panel allow infrastructure blocking.
- Recovery requires backups, not payment.

## Lessons

- Ransomware configuration is as valuable as the sample.
- `floss` and `capa` speed up obfuscated binary triage.
- Mutexes and extensions help detect variants.
- Document IOCs without publishing keys or victim data.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://blog.w4nders.sg/writeups/sherlockLockpick4>
- <https://attack.mitre.org/techniques/T1486/>
