---
challenge: APKey
type: Mobile
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, apk, smali, md5, authentication-bypass]
---

# APKey — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Una app Android valida la contraseña comparando su MD5 con un hash embebido. El hash no protege nada: se parchea la comparación en smali o se recompila la app para aceptar cualquier entrada. La clave de descifrado y la flag están en el propio APK.

## Enunciado y superficie

- Mobile, Very Easy, retirado.
- Se entrega `APKey.apk`.
- La app pide usuario y contraseña; un login correcto muestra la flag.

```bash
file APKey.apk
apktool d APKey.apk -o apk
```

## Reconocimiento

- `AndroidManifest.xml` muestra una única actividad principal.
- `jadx` revela una comparación entre el MD5 de la entrada y una cadena de 32 caracteres.
- La cadena no es un secreto criptográfico: está en el código y puede sustituirse.

```bash
jadx -d jadx APKey.apk
grep -RIn 'md5\|MD5\|digest' jadx/sources | head
```

## Análisis

La actividad construye el hash de la contraseña y lo compara con una constante. La rama que muestra la flag se ejecuta cuando la comparación es verdadera. En smali, la condición es un `if-ne` o `if-eqz` fácil de localizar.

```smali
const-string v0, "<MD5>"
invoke-virtual {p0, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z
move-result v1
if-nez v1, :cond_fail
```

## Explotación

1. Localizar el método de validación en `smali/com/example/apkey/MainActivity*.smali`.
2. Cambiar la condición para que siempre siga la rama de éxito, o sustituir el hash por el MD5 de una contraseña conocida.
3. Recompilar, alinear y firmar el APK.
4. Instalarlo en un emulador API 30 o inferior y abrir la sesión.

```bash
apktool b apk -o APKey-patched.apk
zipalign -p 4 APKey-patched.apk APKey-aligned.apk
apksigner sign --ks release.jks APKey-aligned.apk
adb install -r APKey-aligned.apk
```

La app muestra la flag; se redacta en la ficha.

## Evidencia

- Comparación original y parcheada.
- APK firmado e instalado.
- Pantalla de éxito, con la flag redactada.

## Lecciones aprendidas

- Un hash embebido no autentica: solo compara una entrada con un valor fijo.
- La ofuscación de nombres no impide encontrar la comparación.
- Recompilar y firmar es parte del flujo normal de análisis Android.

## Mitigaciones y detección

- No almacenar secretos ni validaciones en el cliente.
- Verificar credenciales en el servidor con un KDF adecuado.
- Usar Play Integrity y ofuscación como defensa en profundidad, no como autenticación.
- Detectar APKs recompiladas por cambios de firma y de hash.

## Referencias

- <https://www.hackthebox.com/challenges/APKey>
- <https://developer.android.com/tools/apksigner>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1552/>
