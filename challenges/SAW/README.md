---
challenge: SAW
type: Mobile
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [mobile, android, smali, root-detection, patching]
---

# SAW — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La app detecta root y bloquea la pantalla de éxito en un emulador. El chequeo está en smali y se puede parchear para que siempre devuelva falso. Al recompilar y firmar, la app muestra la flag.

## Enunciado y superficie

- Mobile, Easy, retirado.
- Se entrega un APK.
- La app se cierra o muestra un error al detectar un dispositivo rooteado.

```bash
apktool d SAW.apk -o saw
jadx -d jadx SAW.apk
```

## Reconocimiento

- `AndroidManifest.xml` declara una actividad principal y posibles comprobaciones de integridad.
- `jadx` muestra métodos con nombres como `isRooted`, `checkRoot` o rutas de `su`.
- La detección se ejecuta antes de mostrar el contenido.

```bash
grep -RInE 'isRooted|checkRoot|/system/bin/su|test-keys|superuser' jadx/sources saw/smali | head -n 30
```

## Análisis

El método devuelve un booleano a partir de varias comprobaciones: binarios `su`, propiedades del build y paquetes de superusuario. La actividad consulta ese valor y decide si continúa.

En smali, el retorno se localiza por `return v0` dentro del método de detección o por la condición que salta a la pantalla de error.

## Explotación

1. Localizar el método de detección en smali.
2. Sustituir su cuerpo por un retorno constante `false`, o invertir la condición en la actividad.
3. Recompilar, alinear y firmar.
4. Instalar en el emulador y abrir la app.

```bash
apktool b saw -o SAW-patched.apk
zipalign -p 4 SAW-patched.apk SAW-aligned.apk
apksigner sign --ks release.jks SAW-aligned.apk
adb install -r SAW-aligned.apk
```

La pantalla de éxito muestra la flag; se redacta en la ficha.

## Evidencia

- Método original y parcheado.
- APK firmado e instalado.
- Pantalla de éxito, con la flag redactada.

## Lecciones aprendidas

- La detección de root en el cliente se puede desactivar.
- Parchear un único retorno es suficiente si la comprobación está centralizada.
- Recompilar exige volver a firmar; la firma original deja de ser válida.

## Mitigaciones y detección

- No usar la detección de root como control de seguridad.
- Validar en servidor y usar Play Integrity.
- Ofuscar y dispersar las comprobaciones.
- Detectar cambios de firma y de integridad del APK.

## Referencias

- <https://www.hackthebox.com/challenges/SAW>
- <https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/>
- <https://developer.android.com/tools/apksigner>
- <https://attack.mitre.org/techniques/T1552/>
