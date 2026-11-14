---
challenge: Anti Flag
type: Reversing
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [reversing, elf, rc4, anti-debug, ghidra]
---

# Anti Flag — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

The binary checks input and hides the flag in RC4-encrypted data. Static analysis locates the decryption call and embedded key; decrypting the `.rodata` block reveals the flag without running the binary.

## Statement and surface

- Reversing, Easy, retired.
- A 64-bit ELF is provided.
- The binary has anti-debug checks and compares input.

```bash
file anti_flag
checksec --file=anti_flag
strings -a anti_flag | head
```

## Reconnaissance

- The binary is not stripped.
- `main` calls an RC4 initialization routine.
- The key appears as a string or is built on the stack.
- There are `ptrace` calls or `TracerPid` checks.

## Code analysis

Ghidra/Binary Ninja identifies the RC4 function: 256-byte KSA, PRGA and XOR with the ciphertext. The key `<KEY>` is passed to the routine and the encrypted block sits in `.rodata` at `0x2011`.

## Flaw explanation

The "protection" is obfuscation, not secure cryptography: the key is in the binary and the algorithm is reversible. Anti-debug checks only block dynamic execution, not static analysis.

## Local reproduction

```bash
# Extract the ciphertext and key
python3 - <<'PY'
from binascii import unhexlify
ct = unhexlify('<CIPHERTEXT>')
print(ct)
PY
```

## Exploitation

```python
from Crypto.Cipher import ARC4
ct = bytes.fromhex('<CIPHERTEXT>')
print(ARC4.new(b'<KEY>').decrypt(ct))
```

CyberChef or Binary Ninja's RC4 transform also works. The flag is redacted.

## Evidence

- `file`/`checksec` and relevant strings.
- Identified RC4 function.
- Located ciphertext and key.
- Plaintext without publishing the flag.

## Lessons learned

- RC4 with an embedded key is reversible obfuscation.
- Static analysis bypasses anti-debug traps.
- Key strings may be built on the stack.

## Mitigations and detection

- Do not store secrets in distributed binaries.
- Use authenticated encryption and external keys if protection is required.
- Detect `ptrace` and binaries reading `/proc/self/status`.
- References: NIST RC4, HTB Anti Flag, MITRE T1027.

## References

- <https://www.hackthebox.com/challenges/Anti%20Flag>
- <http://www.0xface1e55.com/posts/reversing/htb/anti_flag>
- <https://attack.mitre.org/techniques/T1027/>
- <https://attack.mitre.org/techniques/T1622/>
