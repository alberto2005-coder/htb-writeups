# Análisis de APK: de `jadx` a Frida

[🇬🇧 English](apk-analysis.en.md) | **Español**

Ruta de trabajo para retos Mobile y para revisar una app Android real: qué descompilar, qué buscar y cómo verlo en ejecución.

## 1. Desempaquetar

```bash
apktool d app.apk -o apktool_out     # recursos + smali
jadx -d jadx_out app.apk             # Java/Kotlin
unzip -l app.apk | grep -E "assets|lib/"
```

- `AndroidManifest.xml` (legible con apktool): actividades exportadas, permisos, `android:debuggable`, `usesCleartextTraffic`.
- `assets/`: bases de datos, JSON, certificados, claves.
- `lib/<abi>/`: código nativo; se revisa con `strings` y Ghidra.
- `res/values/strings.xml`: claves API y endpoints "escondidos".

## 2. Qué buscar

```bash
grep -R -n -i -E "api[_-]?key|secret|token|password|http://|AES|Cipher" jadx_out | head -40
```

- Endpoints y cabeceras de autenticación.
- Cifrado: `Cipher.getInstance`, `SecretKeySpec`, `MessageDigest`.
- Comparaciones de flag: `equals`, `contains`, `startsWith` con cadenas raras.
- Root detection: `superuser.apk`, `su`, `test-keys`, `RootBeer`.
- SSL pinning: `CertificatePinner`, `TrustManager` propio, `network_security_config`.

## 3. Descifrar lo que guarda

```bash
adb shell run-as <paquete> ls -R /data/data/<paquete>
adb pull /data/data/<paquete>/shared_prefs/
```

- `SharedPreferences` en claro o cifradas con una clave del propio código.
- SQLite (`databases/`) con `sqlite3` y `.tables`.
- Ficheros en `files/` y `cache/`.

## 4. Ejecución dinámica

```bash
adb install app.apk
adb logcat | grep -i -E "flag|cipher|token"
```

Frida para saltar root detection y ver valores:

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

`objection -g <paquete> explore` automatiza `android root disable` y `android sslpinning disable`.

## 5. Nativo y ofuscación

- `strings libnative.so | grep -i flag`
- Ghidra sobre `.so`; buscar `JNI_OnLoad` y las funciones exportadas.
- Ofuscación: nombres `a.b.c`; seguir el flujo desde `onCreate` y usar Frida para no leer todo.
- APK con `split`/`bundle`: instalar todos los splits o extraer el `base.apk`.

## Errores típicos

- **`jadx` sin la clase** → está en un `dex` secundario o en nativo.
- **La app cierra al arrancar** → root detection; usa Frida/objection.
- **`BadPaddingException`** → modo o padding mal copiados, o clave en hex y no en base64.
- **`INSTALL_FAILED_NO_MATCHING_ABIS`** → emulador x86 con `.so` solo ARM; usa un dispositivo ARM o un emulador con traducción.

MITRE: T1409, T1521.001, T1633.
