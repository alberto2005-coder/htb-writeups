---
challenge: Cryptohorrific
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, apk, aes, jadx]
---

# Cryptohorrific — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

## Brief

An Android APK stores the flag encrypted. The key ships inside the package, so the task is to decompile, find the encryption and reproduce it.

## Triage

```bash
file app.apk
unzip -l app.apk | head
apktool d app.apk -o apk_out
jadx -d jadx_out app.apk
```

- `apktool` gives resources and a readable `AndroidManifest.xml`.
- `jadx` gives decompiled Java/Kotlin, where the logic lives.

## Locate the encryption

```bash
grep -R -n -i "AES\|Cipher\|SecretKey\|encrypt\|decrypt" jadx_out | head -30
```

Typical patterns:

```java
SecretKeySpec key = new SecretKeySpec("...".getBytes(), "AES");
Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
```

The key may live in `strings.xml`, a constant, `BuildConfig` or `assets/`. It can also be native (`lib/…/libnative.so`), reviewed with `strings` and Ghidra.

## Reproduce the decryption

```python
from Crypto.Cipher import AES
import base64
ct = base64.b64decode('<blob>')
c = AES.new(b'<16 bytes>', AES.MODE_ECB)
print(c.decrypt(ct))
```

For CBC the IV is often the first 16 bytes or a constant in code; for GCM you need `nonce` and `tag`.

## Check at runtime

```bash
adb install app.apk
adb logcat | grep -i "flag\|cipher"
```

Frida hooks `Cipher.doFinal` without decompiling everything:

```javascript
Java.perform(function () {
  var C = Java.use('javax.crypto.Cipher');
  C.doFinal.overload('[B').implementation = function (b) {
    console.log('in ', b);
    var r = this.doFinal(b);
    console.log('out', r);
    return r;
  };
});
```

## Typical errors

- **`jadx` cannot find the key** → it is native or fetched from a server; check `assets/` and `.so`.
- **`BadPaddingException`** → wrong mode/padding or key encoding (hex vs base64).
- **The key looks like text but does not decrypt** → it may be a hash; try MD5/SHA-256 of the string as key.
- **Obfuscation** → names like `a.b.c`; follow the flow from `onCreate` and use Frida for runtime values.

## Lessons

- A key in the client is not a secret: anyone with the APK gets it.
- Mode and padding are in the code; copying them wrong is the most common failure.
- Frida saves hours when obfuscation makes the decompiled code unreadable.

MITRE: T1409, T1521.
