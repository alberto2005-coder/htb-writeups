---
topic: Android instrumentation
tags: [mobile, android, frida, smali, root-detection, ssl-hook, instrumentation]
---

# Android instrumentation

**English** | [🇪🇸 Español](android-instrumentation.md)

## Concept

Dynamic instrumentation modifies a running app without recompiling it. Frida hooks Java methods and native functions; smali patching changes bytecode before rebuilding the APK. It is the usual path for bypassing root detection, validations and pinning.

## When it applies

- An app with root detection or integrity checks.
- Password validation on the client.
- Java or native pinning.
- A need to observe arguments and return values.

## Procedure

1. Decompile with `apktool` and locate the check.
2. Choose smali patching or dynamic hooking.
3. Run `frida-server` with root permissions.
4. Hook the method or native function.
5. Verify the flow changes and the app remains stable.

```bash
apktool d app.apk -o app
grep -RInE 'isRooted|su|frida|if-eqz|if-ne' app/smali | head
frida -U -f <PACKAGE> -l hook.js --no-pause
```

```javascript
Java.perform(function () {
  var Root = Java.use('com.scottyab.rootbeer.RootBeer');
  Root.isRooted.implementation = function () { return false; };
});
```

## Variants

- Smali patching with `if-eqz`/`if-ne` and rebuilding.
- Hooking `SSL_CTX_set_cert_verify_callback`.
- Bypassing `RootBeer`, `SafetyNet` or custom checks.
- Using `objection` for common tasks.

## Limitations

- Some apps detect Frida or a modified environment.
- Native pinning requires locating the right function.
- Rebuilding invalidates the original signature.
- Old emulators simplify or change behaviour.

## Mitigation and detection

- Combine root detection with integrity attestation.
- Obfuscate and spread the checks.
- Verify the signature, APK and native libraries.
- Detect Frida, hooks and proxies in telemetry.

## References

- <https://frida.re/docs/android/>
- <https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/>
- <https://github.com/sensepost/objection>
