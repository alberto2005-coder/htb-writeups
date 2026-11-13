---
topic: React Native analysis
tags: [mobile, android, react-native, javascript, hermes, bundle]
---

# React Native analysis

**English** | [🇪🇸 Español](react-native-analysis.md)

## Concept

A React Native app includes its JavaScript logic, usually in `assets/index.android.bundle`. The bundle is packaged but not encrypted: it can be extracted, beautified and searched for strings, comparisons and keys. Modern builds may use Hermes bytecode.

## When it applies

- An APK with `assets/index.android.bundle`.
- Obfuscated or minified strings.
- Licence or password validation on the client.
- Embedded API secrets.

## Procedure

1. Unzip the APK and locate the bundle.
2. Identify plain JavaScript or Hermes.
3. Beautify or decompile the bundle.
4. Search for validations, URLs and keys.
5. Confirm the flow in the app or through instrumentation.

```bash
unzip app.apk -d apk
find apk/assets -maxdepth 2 -type f
npx js-beautify apk/assets/index.android.bundle -o bundle.js
grep -nE 'password|secret|token|https?://' bundle.js | head
```

## Variants

- Hermes bytecode (`HBC`) with `hbctool` or `hermes-dec`.
- A bundle split across multiple files.
- Obfuscation with short names and encoded strings.
- Critical logic in a native module.

## Limitations

- Hermes cannot be read as JavaScript directly.
- The bundle may be encrypted or split.
- The app may validate package integrity.
- An embedded secret may be a public key with no offensive value.

## Mitigation and detection

- Do not embed secrets in the bundle.
- Validate on the server and sign responses.
- Obfuscate without treating it as a security control.
- Monitor APK extraction and abnormal API use.

## References

- <https://reactnative.dev/docs/performance>
- <https://github.com/bongtrop/hbctool>
- <https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/>
