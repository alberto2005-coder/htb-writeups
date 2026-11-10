---
challenge: Cryptohorrific
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, ios, aes, plist, cccrypt, hopper]
---

# Cryptohorrific — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

## TL;DR

**It is not Android: it is an iOS app.** You get an `.app` bundle with a Mach-O binary and a `challenge.plist` holding a base64 blob. `ViewController` calls `CCCrypt` with the key and IV in clear; replaying that AES outside the app yields the flag.

## Brief

"Secure coding is the keystone of the application security!" Category Mobile. The bundle (`hackthebox.app`) ships its `Info.plist`, resources and a 64-bit Mach-O executable.

## Triage

```bash
unzip -l Cryptohorrific.zip
file hackthebox.app/hackthebox          # Mach-O 64-bit x86_64
plistutil -i hackthebox.app/challenge.plist -o challenge.xml
cat challenge.xml
```

The plist has three fields (`title`, `id`, `flag`); `flag` is a long base64 string. `plistutil` (or Python's `plistlib`) turns it into readable XML.

## Locate the encryption

```bash
strings -a hackthebox.app/hackthebox | grep -iE 'key|iv|CCCrypt|AES'
```

The binary is Mach-O and calls **`CCCrypt`** (CommonCrypto). In Hopper/IDA, following `-[ViewController viewDidLoad]`, the key and IV appear as literals:

```text
key = !A%D*G-KaPdSgVkY
iv  = QfTjWnZq4t7w!z%C
```

## Root cause

The key lives **in the client**. Anyone with the bundle extracts it in minutes, so the encryption only buys obfuscation. The effective mode is AES-128-**ECB**, unauthenticated: the IV is in the code but protects nothing.

## Reproduce the decryption

```python
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

ct = base64.b64decode("<blob from the plist>")
k = b"!A%D*G-KaPdSgVkY"
print(unpad(AES.new(k, AES.MODE_ECB).decrypt(ct), 16).decode())
```

Equivalent with OpenSSL:

```bash
echo "<blob>" | base64 -d | \
  openssl enc -d -aes-128-ecb -nopad -K "$(printf '%s' '!A%D*G-KaPdSgVkY' | xxd -p)"
```

## Exploitation

1. Extract the bundle and convert the plist to XML.
2. Identify the base64 blob in the `flag` field.
3. Find `CCCrypt` and its arguments in the Mach-O.
4. Decrypt locally with the key (ECB ignores the IV).

## Evidence

- `challenge.plist` with the base64 blob (redacted).
- `strings`/Hopper showing `CCCrypt` and the key literals.
- Plaintext in `HTB{...}` form.

## Lessons

- **iOS, not Android**: a ZIP with `Info.plist` and a Mach-O will not open in `jadx`; use Hopper/IDA/radare2 plus `plistutil`.
- **`CCCrypt` is the entry point**: almost all Apple symmetric crypto goes through it.
- **ECB ignores the IV**: if the result does not match while trying CBC, check the mode before rebuilding the key.
- A key inside a binary is not a secret, just an inconvenience.

## Mitigation

- Never encrypt secrets with embedded keys: the binary is public by definition.
- If client-side crypto is unavoidable, derive keys per user, verify server-side and use AES-GCM with a nonce; never ECB.
- Review: grep for `CCCrypt`/`kCCAlgorithmAES` with literal keys in the binary.

## References

- [MITRE T1409](https://attack.mitre.org/techniques/T1409/)
- [MITRE T1521](https://attack.mitre.org/techniques/T1521/)
- [apk-analysis](../../knowledge/mobile/apk-analysis.md)
