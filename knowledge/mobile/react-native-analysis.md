---
topic: React Native analysis
tags: [mobile, android, react-native, javascript, hermes, bundle]
---

# React Native analysis

[🌐 English](react-native-analysis.en.md) | **Español**

## Concepto

Una app React Native incluye su lógica en JavaScript, normalmente en `assets/index.android.bundle`. El bundle está empaquetado pero no cifrado: se puede extraer, embellecer y buscar cadenas, comparaciones y claves. En builds modernas puede estar compilado con Hermes.

## Cuándo aplica

- APK con `assets/index.android.bundle`.
- Cadenas ofuscadas o minificadas.
- Validación de licencias o contraseñas en cliente.
- Secretos de API embebidos.

## Procedimiento

1. Descomprimir el APK y localizar el bundle.
2. Identificar si es JavaScript plano o Hermes.
3. Embellecer o descompilar el bundle.
4. Buscar validaciones, URLs y claves.
5. Confirmar el flujo en la app o con instrumentación.

```bash
unzip app.apk -d apk
find apk/assets -maxdepth 2 -type f
npx js-beautify apk/assets/index.android.bundle -o bundle.js
grep -nE 'password|secret|token|https?://' bundle.js | head
```

## Variantes

- Hermes bytecode (`HBC`) con `hbctool` o `hermes-dec`.
- Bundle dividido en varios archivos.
- Ofuscación con nombres cortos y strings codificados.
- Lógica crítica en un módulo nativo.

## Limitaciones

- Hermes no se lee como JavaScript directamente.
- El bundle puede estar cifrado o dividido.
- La app puede validar la integridad del paquete.
- Un secreto embebido puede ser una clave pública sin valor ofensivo.

## Mitigación y detección

- No incluir secretos en el bundle.
- Validar en servidor y firmar respuestas.
- Ofuscar sin confiar en la ofuscación como control.
- Monitorizar extracción de APKs y uso anómalo de APIs.

## Referencias

- <https://reactnative.dev/docs/performance>
- <https://github.com/bongtrop/hbctool>
- <https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/>
