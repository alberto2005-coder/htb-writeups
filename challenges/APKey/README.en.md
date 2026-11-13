---
challenge: APKey
type: Mobile
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, apk, smali, md5, authentication-bypass]
---

# APKey — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

An Android app checks the password by comparing its MD5 with an embedded hash. The hash protects nothing: the comparison is patched in smali or the app is rebuilt to accept any input. The decryption key and flag are inside the APK.

## Prompt and surface

- Mobile, Very Easy, retired.
- `APKey.apk` is provided.
- The app asks for a username and password; a successful login shows the flag.

```bash
file APKey.apk
apktool d APKey.apk -o apk
```

## Reconnaissance

- `AndroidManifest.xml` shows a single main activity.
- `jadx` reveals a comparison between the input's MD5 and a 32-character string.
- The string is not a cryptographic secret: it lives in code and can be replaced.

```bash
jadx -d jadx APKey.apk
grep -RIn 'md5\|MD5\|digest' jadx/sources | head
```

## Analysis

The activity hashes the password and compares it with a constant. The branch that shows the flag runs when the comparison is true. In smali, the condition is an `if-ne` or `if-eqz` that is easy to locate.

```smali
const-string v0, "<MD5>"
invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
move-result v1
if-nez v1, :cond_fail
```

## Exploitation

1. Locate the validation method in `smali/com/example/apkey/MainActivity*.smali`.
2. Change the condition to always take the success branch, or replace the hash with the MD5 of a known password.
3. Rebuild, align and sign the APK.
4. Install it on an API 30 or lower emulator and log in.

```bash
apktool b apk -o APKey-patched.apk
zipalign -p 4 APKey-patched.apk APKey-aligned.apk
apksigner sign --ks release.jks APKey-aligned.apk
adb install -r APKey-aligned.apk
```

The app displays the flag; it is redacted here.

## Evidence

- Original and patched comparison.
- Signed and installed APK.
- Success screen, with the flag redacted.

## Lessons learned

- An embedded hash does not authenticate: it compares input with a fixed value.
- Name obfuscation does not hide the comparison.
- Rebuilding and signing is part of normal Android analysis.

## Mitigations and detection

- Do not store secrets or validation logic on the client.
- Verify credentials server-side with a proper KDF.
- Use Play Integrity and obfuscation as defence in depth, not as authentication.
- Detect rebuilt APKs through signature and hash changes.

## References

- <https://www.hackthebox.com/challenges/APKey>
- <https://developer.android.com/tools/apksigner>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1552/>
