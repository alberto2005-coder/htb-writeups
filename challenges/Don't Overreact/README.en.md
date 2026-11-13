---
challenge: Don't Overreact
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, react-native, javascript, hardcoded-secret]
---

# Don't Overreact — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The app is built with React Native. Logic and secrets travel in `index.android.bundle`, packaged but unencrypted JavaScript. Unpacking and beautifying it recovers the validation and the flag.

## Prompt and surface

- Mobile, Easy, retired.
- An APK is provided.
- The app shows a screen that asks for input and validates the result.

```bash
unzip -l app.apk | head -n 30
```

## Reconnaissance

- The APK contains `assets/index.android.bundle`, typical of React Native.
- The bundle is minified JavaScript; it is not compiled to Android bytecode.
- `strings` already reveals paths and possible validation strings.

```bash
unzip -p app.apk assets/index.android.bundle > index.android.bundle
file index.android.bundle
npx js-beautify index.android.bundle > bundle.pretty.js
```

## Analysis

The comparison logic and the strings involved are located. React Native commonly keeps validation, the key and the success message in the same module.

```bash
grep -nE 'flag|secret|check|validate|atob|decrypt' bundle.pretty.js | head -n 40
```

If the value is encoded, the decoding function is reproduced in Node instead of running the app.

```bash
node -e "console.log(Buffer.from('<BASE64>','base64').toString())"
```

## Exploitation

1. Extract the bundle from the APK.
2. Beautify it and locate the success decision.
3. Identify the expected input or the inverse transformation.
4. Enter it in the app or calculate the flag directly.

No APK patching or signature change is needed.

## Evidence

- Bundle path and size.
- Snippet of the validation function.
- Calculated input and success screen, with the flag redacted.

## Lessons learned

- React Native does not hide logic: it only packages it.
- Minification is not strong obfuscation.
- Client-side secrets are public by definition.

## Mitigations and detection

- Do not include keys or definitive validation in the bundle.
- Validate server-side and use app attestation.
- Obfuscate and split code as defence in depth.
- Detect modified bundles and unexpected signatures.

## References

- <https://www.hackthebox.com/challenges/Don%27t%20Overreact>
- <https://reactnative.dev/docs/performance>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1552/>
