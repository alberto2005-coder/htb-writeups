---
topic: Android certificate pinning
tags: [mobile, android, certificate-pinning, frida, okhttp, tls]
---

# Android certificate pinning

**English** | [🇪🇸 Español](android-certificate-pinning.md)

## Concept

Certificate pinning requires the server certificate or public key to match a known value. On Android it is implemented in Java/Kotlin (`TrustManager`, OkHttp `CertificatePinner`) or in a native library with OpenSSL/BoringSSL. It prevents accepting any CA in the device store, but does not prevent process instrumentation.

## When it applies

- Intercepting mobile app traffic.
- Analysing an API that rejects the proxy certificate.
- Reviewing client-side defences.
- Challenges involving `pinning`, `anchoring` or `network security config`.

## Requirements and conditions

- APK or installed app on a controlled emulator.
- Proxy with a custom CA.
- Frida or a patching environment.
- Ability to restart the app and modify its network configuration.

## Procedure

1. Decompile and search for `CertificatePinner`, `TrustManager` and `network_security_config`.
2. Review native libraries with `strings`, `readelf` and Ghidra.
3. Install the proxy CA on the device.
4. Hook every validation layer, not just one.
5. Confirm the request reaches the proxy and the response is processed.

```javascript
Java.perform(function () {
  var Pinner = Java.use('okhttp3.CertificatePinner');
  Pinner.check.overload('java.lang.String', 'java.util.List').implementation = function () {};
});
```

## Variants

- Leaf-certificate or public-key pin.
- Pin in `network_security_config.xml`.
- Native pin with `SSL_CTX_set_cert_verify_callback`.
- Pinning combined with attestation and obfuscation.

## Limitations

- A client-side pin can always be disabled through instrumentation.
- Hooking only OkHttp leaves the `TrustManager` or native layer active.
- Some apps detect Frida, proxies or user certificates.
- An old emulator may not reproduce real-device behaviour.

## Mitigation

- Combine pinning with integrity attestation.
- Obfuscate and spread the checks.
- Do not make the client the sole authentication decision.
- Rotate pins and monitor validation failures.

## Detection

- Alert on repeated TLS errors from one account.
- Detect proxies, user CAs and instrumentation processes.
- Compare APK fingerprints with the published build.
- Review integrity and attestation telemetry.

## References

- <https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/>
- <https://square.github.io/okhttp/features/https/>
- <https://frida.re/docs/android/>
- <https://developer.android.com/privacy-and-security/security-config>
