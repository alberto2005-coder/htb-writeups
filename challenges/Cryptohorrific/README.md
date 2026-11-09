---
challenge: Cryptohorrific
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, apk, aes, jadx]
---

# Cryptohorrific — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

- Ver las secciones adyacentes para el detalle.

## Enunciado y superficie

APK de Android que guarda la flag cifrada. La clave está en el propio paquete, así que el reto es descompilar, localizar el cifrado y reproducirlo.

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

[🇬🇧 English](README.en.md) | **Español**

## Reproducción local

- Emulador Android con la misma API o dispositivo físico; instala con `adb install`.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **`jadx` no encuentra la clave** → está en nativo o llega del servidor; revisa `assets/` y `.so`.
- **`BadPaddingException`** → modo/padding equivocado o clave mal codificada (hex vs base64).
- **La clave parece texto pero no descifra** → puede ser un hash; prueba MD5/SHA-256 de la cadena como clave.
- **Ofuscación** → nombres como `a.b.c`; sigue el flujo desde `onCreate` y usa Frida para ver valores en runtime.

- Una clave en el cliente no es secreto: cualquiera con el APK la obtiene.
- El modo y el padding están en el código; copiarlos mal es el fallo más común.
- Frida ahorra horas cuando la ofuscación hace ilegible el decompilado.

MITRE: T1409, T1521.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [MITRE T1409](https://attack.mitre.org/techniques/T1409/)
- [MITRE T1521](https://attack.mitre.org/techniques/T1521/)
- [apk-analysis](../../knowledge/mobile/apk-analysis.md)
## Triaje

```bash
file app.apk
unzip -l app.apk | head
apktool d app.apk -o apk_out
jadx -d jadx_out app.apk
```

- `apktool` da recursos y `AndroidManifest.xml` legible.
- `jadx` da el código Java/Kotlin decompilado, que es donde está la lógica.

## Localizar el cifrado

```bash
grep -R -n -i "AES\|Cipher\|SecretKey\|encrypt\|decrypt" jadx_out | head -30
```

Patrones típicos:

```java
SecretKeySpec key = new SecretKeySpec("...".getBytes(), "AES");
Cipher c = Cipher.getInstance("AES/ECB/PKCS5Padding");
```

La clave puede estar en `strings.xml`, en una constante, en `BuildConfig` o en `assets/`. También en nativo (`lib/…/libnative.so`), que se revisa con `strings` y Ghidra.

## Reproducir el descifrado

```python
from Crypto.Cipher import AES
import base64
ct = base64.b64decode('<blob>')
c = AES.new(b'<16 bytes>', AES.MODE_ECB)
print(c.decrypt(ct))
```

Si el modo es CBC, el IV suele estar en los primeros 16 bytes o en una constante del código; si es GCM, hacen falta `nonce` y `tag`.

## Comprobar en ejecución

```bash
adb install app.apk
adb logcat | grep -i "flag\|cipher"
```

Con Frida se intercepta `Cipher.doFinal` sin descompilar todo:

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
