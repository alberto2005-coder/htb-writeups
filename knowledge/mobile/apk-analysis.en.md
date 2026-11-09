# APK analysis: from `jadx` to Frida

**English** | [🇪🇸 Español](apk-analysis.md)

Workflow for Mobile challenges and for reviewing a real Android app: what to decompile, what to look for and how to watch it at runtime.

## 1. Unpack

```bash
apktool d app.apk -o apktool_out     # resources + smali
jadx -d jadx_out app.apk             # Java/Kotlin
unzip -l app.apk | grep -E "assets|lib/"
```

- `AndroidManifest.xml` (readable with apktool): exported activities, permissions, `android:debuggable`, `usesCleartextTraffic`.
- `assets/`: databases, JSON, certificates, keys.
- `lib/<abi>/`: native code; review with `strings` and Ghidra.
- `res/values/strings.xml`: API keys and "hidden" endpoints.

## 2. What to look for

```bash
grep -R -n -i -E "api[_-]?key|secret|token|password|http://|AES|Cipher" jadx_out | head -40
```

- Endpoints and auth headers.
- Crypto: `Cipher.getInstance`, `SecretKeySpec`, `MessageDigest`.
- Flag comparisons: `equals`, `contains`, `startsWith` with odd strings.
- Root detection: `superuser.apk`, `su`, `test-keys`, `RootBeer`.
- SSL pinning: `CertificatePinner`, custom `TrustManager`, `network_security_config`.

## 3. Decrypt what it stores

```bash
adb shell run-as <package> ls -R /data/data/<package>
adb pull /data/data/<package>/shared_prefs/
```

- `SharedPreferences` in clear or encrypted with a key from the code itself.
- SQLite (`databases/`) with `sqlite3` and `.tables`.
- Files under `files/` and `cache/`.

## 4. Dynamic execution

```bash
adb install app.apk
adb logcat | grep -i -E "flag|cipher|token"
```

Frida to bypass root detection and watch values:

```javascript
Java.perform(function () {
  var C = Java.use('javax.crypto.Cipher');
  C.doFinal.overload('[B').implementation = function (b) {
    console.log('in', b); var r = this.doFinal(b); console.log('out', r); return r;
  };
  var B = Java.use('android.os.Build');
  B.TAGS.value = 'release-keys';
});
```

`objection -g <package> explore` automates `android root disable` and `android sslpinning disable`.

## 5. Native code and obfuscation

- `strings libnative.so | grep -i flag`
- Ghidra on the `.so`; look for `JNI_OnLoad` and exported functions.
- Obfuscation: names like `a.b.c`; follow the flow from `onCreate` and use Frida instead of reading everything.
- Split/bundle APKs: install all splits or extract `base.apk`.

## Typical errors

- **`jadx` misses the class** → it lives in a secondary `dex` or in native code.
- **App closes on start** → root detection; use Frida/objection.
- **`BadPaddingException`** → wrong mode or padding, or key in hex rather than base64.
- **`INSTALL_FAILED_NO_MATCHING_ABIS`** → x86 emulator with ARM-only `.so`; use an ARM device or an emulator with translation.

MITRE: T1409, T1521.001, T1633.
