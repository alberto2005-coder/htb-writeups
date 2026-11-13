---
challenge: SAW
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, smali, root-detection, patching]
---

# SAW — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The app detects root and blocks the success screen in an emulator. The check lives in smali and can be patched to always return false. After rebuilding and signing, the app shows the flag.

## Prompt and surface

- Mobile, Easy, retired.
- An APK is provided.
- The app exits or errors when it detects a rooted device.

```bash
apktool d SAW.apk -o saw
jadx -d jadx SAW.apk
```

## Reconnaissance

- `AndroidManifest.xml` declares a main activity and possible integrity checks.
- `jadx` shows methods named like `isRooted`, `checkRoot` or `su` paths.
- Detection runs before content is displayed.

```bash
grep -RInE 'isRooted|checkRoot|/system/bin/su|test-keys|superuser' jadx/sources saw/smali | head -n 30
```

## Analysis

The method returns a boolean based on several checks: `su` binaries, build properties and superuser packages. The activity reads that value and decides whether to continue.

In smali, the return is located by `return v0` inside the detection method or by the branch to the error screen.

## Exploitation

1. Locate the detection method in smali.
2. Replace its body with a constant `false` return, or invert the branch in the activity.
3. Rebuild, align and sign.
4. Install on the emulator and open the app.

```bash
apktool b saw -o SAW-patched.apk
zipalign -p 4 SAW-patched.apk SAW-aligned.apk
apksigner sign --ks release.jks SAW-aligned.apk
adb install -r SAW-aligned.apk
```

The success screen shows the flag; it is redacted here.

## Evidence

- Original and patched method.
- Signed and installed APK.
- Success screen, with the flag redacted.

## Lessons learned

- Client-side root detection can be disabled.
- Patching one return is enough when the check is centralised.
- Rebuilding requires re-signing; the original signature is no longer valid.

## Mitigations and detection

- Do not use root detection as a security control.
- Validate server-side and use Play Integrity.
- Obfuscate and spread the checks.
- Detect signature and APK integrity changes.

## References

- <https://www.hackthebox.com/challenges/SAW>
- <https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/>
- <https://developer.android.com/tools/apksigner>
- <https://attack.mitre.org/techniques/T1552/>
