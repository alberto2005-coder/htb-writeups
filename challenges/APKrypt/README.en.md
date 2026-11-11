---
challenge: APKrypt
category: Challenge
type: mobile
os: Android
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, apk, smali, aes, hardcoded-key, jadx]
---

# APKrypt — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no real flags or credentials.

## TL;DR

An Android APK asking for a VIP code that, when its MD5 matches a value in the code, decrypts a base64 blob. The AES key is also in the binary and the mode is ECB, so there is nothing to break: decompile, read the key, decrypt the blob and the flag appears.

## Prompt and surface

- **Mobile** category, **Easy** difficulty.
- Ships `APKrypt.apk` and a `README` asking for API 29 or lower.
- No emulator needed: the analysis is static.

```bash
file APKrypt.apk
apktool decode APKrypt.apk -o apkrypt_src
```

## Recon

```bash
grep -ril "vip\|aes\|md5" apkrypt_src/smali | head
```

`AndroidManifest.xml` declares a single activity. In `smali/com/example/apkrypt/MainActivity.smali` the hash comparison and the call to `generateKey()` appear, and that method returns a fixed key.

## Code analysis

```bash
d2j-smali apkrypt_src/smali/com/example/apkrypt/*.smali -o out.dex
d2j-dex2jar out.dex -o apkrypt.jar
jd-gui apkrypt.jar
```

In the decompiled code:

- The button computes `MD5(code)` and compares it with `735c3628699822c4c1c09219f317a8e9`.
- On match it decrypts the base64 string `k+RLD5J86JRYnluaZLF3Zs/yJrVdVfGo1CQy5k0+tCZDJZTozBWPn2lExQYDHH1l`.
- `generateKey()` generates nothing: it returns `new SecretKeySpec("Dgu8Trf6Ge4Ki9Lb".getBytes(), "AES")`.
- The cipher is instantiated as `AES/ECB/PKCS5Padding`, with no IV.

## Why it fails

Two decisions turn it into a reading exercise: the key sits in code and ECB uses no IV. The "VIP code" only controls whether the decryption branch runs; it does not protect the secret.

```text
key    = Dgu8Trf6Ge4Ki9Lb  (16 bytes, AES-128)
mode   = ECB, PKCS#5/7 padding
data   = base64 of 64 bytes -> 3 blocks + padding
```

## Local reproduction

```python
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

ct = b64decode("k+RLD5J86JRYnluaZLF3Zs/yJrVdVfGo1CQy5k0+tCZDJZTozBWPn2lExQYDHH1l")
pt = AES.new(b"Dgu8Trf6Ge4Ki9Lb", AES.MODE_ECB).decrypt(ct)
print(unpad(pt, 16).decode())
```

## Exploitation

1. `apktool d` and locate `MainActivity`.
2. Grab the key and blob with `grep` or jadx.
3. Decrypt with the script above.
4. Submit the result where the challenge asks.

There is no need to compute the MD5: the code only compares, it does not derive the key from the code.

## Evidence

- Screenshot of the decompiled code with key and blob redacted.
- Script output with the flag partially hidden.

## Lessons learned

- A client-side integrity check does not protect a secret: the key sits next to it.
- ECB leaks patterns and offers no real confidentiality; here the key is fixed as well.
- `apktool` plus jadx is enough for unobfuscated apps; Frida is not always needed.
- The "VIP code" was a hint, not the protection.

## Mitigations and detection

- Never embed keys in the APK; use the Keystore and per-device key derivation.
- Use AES-GCM with a random nonce instead of ECB.
- Obfuscate and verify integrity server-side, not in the client.
- Detection: APKs with long base64 strings and 16-byte constants, `SecretKeySpec` with literals and no `SecureRandom`.
- References: OWASP MASVS-CRYPTO, CWE-321 (hard-coded key).

## References

- <https://www.hackthebox.com/challenges/apkrypt>
- <https://bryanmcnulty.com/posts/htb-apkrypt>
- <https://dua2z3rr.github.io/posts/APKrypt-Walkthrough>
- <https://mas.owasp.org/MASVS/05-MASVS-CRYPTO/>
