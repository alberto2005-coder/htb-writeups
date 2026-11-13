---
challenge: Pinned
type: Mobile
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [mobile, android, certificate-pinning, frida, okhttp, interception]
---

# Pinned — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The app uses certificate pinning and only allows automatic login. The pin is enforced client-side, so a Frida hook over `TrustManager` and `CertificatePinner` removes validation. Intercepting traffic recovers the credential and the flag.

## Prompt and surface

- Mobile, Medium, retired.
- `pinned.apk` and a `README.txt` are provided.
- The app requires Android 10 or lower to install the APK.

```bash
apktool d pinned.apk -o pinned
jadx -d jadx pinned.apk
```

## Reconnaissance

- `AndroidManifest.xml` declares `usesCleartextTraffic` and a login activity.
- `jadx` shows OkHttp and a class using `CertificatePinner`.
- The pin compares the server certificate with an embedded hash.

```bash
grep -RInE 'CertificatePinner|TrustManager|sha256/|pin' jadx/sources | head -n 30
```

## Analysis

Pinning is implemented in two layers: the custom `TrustManager` and OkHttp's `CertificatePinner`. Blocking only one leaves the other active. A Frida hook can replace both with permissive checks.

```javascript
Java.perform(function () {
  var Pinner = Java.use('okhttp3.CertificatePinner');
  Pinner.check.overload('java.lang.String', 'java.util.List').implementation = function () {};
});
```

## Exploitation

1. Start an API 29 or lower emulator with `frida-server`.
2. Run the app with the bypass script.
3. Configure a proxy and install the Burp or mitmproxy certificate.
4. Log in and capture the request.

```bash
frida -U -f <PACKAGE> -l bypass.js --no-pause
```

The login response contains the flag or a credential that leads to it.

## Evidence

- Pinning class and bypass script.
- Intercepted request and response, with tokens redacted.
- Success screen, with the flag redacted.

## Lessons learned

- Client-side pinning does not prevent dynamic analysis.
- Every validation layer must be disabled, not just one.
- An emulator on an older Android release makes instrumentation easier.

## Mitigations and detection

- Combine pinning with attestation and obfuscation.
- Do not let the client decide login success.
- Detect Frida, proxies and user certificates.
- Rotate pins and monitor validation failures.

## References

- <https://www.hackthebox.com/challenges/Pinned>
- <https://frida.re/docs/android/>
- <https://square.github.io/okhttp/features/https/>
- <https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/>
