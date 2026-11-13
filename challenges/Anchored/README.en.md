---
challenge: Anchored
type: Mobile
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [mobile, android, native-library, certificate-anchoring, frida, ssl]
---

# Anchored — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The app anchors trust to a specific certificate inside a native library. Pinning is not in Java but in C/C++. The verification function is instrumented with Frida, or the library is patched, to accept the proxy certificate and read the response.

## Prompt and surface

- Mobile, Medium, retired.
- An APK with a native library is provided.
- The app requires Android 10 or lower to install.

```bash
unzip -l anchored.apk | grep -Ei '\.so|lib/'
jadx -d jadx anchored.apk
```

## Reconnaissance

- The APK includes `lib/*/libnative-lib.so`.
- `jadx` shows the library loaded with `System.loadLibrary`.
- Certificate validation happens in native code, not in `TrustManager`.

```bash
strings -a lib/arm64-v8a/libnative-lib.so | grep -Ei 'ssl|verify|cert|pin|openssl'
```

## Analysis

The library uses OpenSSL or BoringSSL and a verification function that compares the certificate with an embedded fingerprint. Symbols may be hidden; `nm`, `readelf` and Ghidra help locate the call.

```bash
readelf -Ws libnative-lib.so | grep -Ei 'SSL|X509|verify'
```

## Exploitation

1. Run an API 29 or lower emulator with `frida-server`.
2. Hook `SSL_CTX_set_cert_verify_callback` or the comparison function to return success.
3. Install the proxy certificate and redirect traffic.
4. Log in and capture the response.

```javascript
Interceptor.attach(Module.findExportByName('libssl.so', 'SSL_CTX_set_cert_verify_callback'), {
  onEnter: function (args) { args[1] = new NativeCallback(function () { return 1; }, 'int', ['pointer', 'pointer']); }
});
```

The flag appears in the response or on the success screen.

## Evidence

- Library and relevant symbols.
- Instrumentation script.
- Request and response, with tokens redacted.
- Redacted flag.

## Lessons learned

- Native pinning is not immune to instrumentation.
- The real TLS library must be identified, not just Java classes.
- An older emulator simplifies loading `frida-server`.

## Mitigations and detection

- Combine native pinning with attestation and obfuscation.
- Verify APK and library integrity.
- Detect Frida, hooks and proxies.
- Do not make the client the sole authentication decision.

## References

- <https://www.hackthebox.com/challenges/Anchored>
- <https://frida.re/docs/functions/>
- <https://www.openssl.org/docs/man3.0/man3/SSL_CTX_set_cert_verify_callback.html>
- <https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/>
