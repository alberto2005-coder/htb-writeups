---
challenge: Anchored
type: Mobile
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [mobile, android, native-library, certificate-anchoring, frida, ssl]
---

# Anchored — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La app ancla la confianza a un certificado concreto en una biblioteca nativa. El pin no está en Java, sino en código C/C++. Se instrumenta la función de verificación con Frida o se parchea la biblioteca para aceptar el certificado del proxy y leer la respuesta.

## Enunciado y superficie

- Mobile, Medium, retirado.
- Se entrega un APK con una biblioteca nativa.
- La app exige Android 10 o inferior para instalar.

```bash
unzip -l anchored.apk | grep -Ei '\.so|lib/'
jadx -d jadx anchored.apk
```

## Reconocimiento

- El APK incluye `lib/*/libnative-lib.so`.
- `jadx` muestra la carga de la biblioteca con `System.loadLibrary`.
- La validación del certificado se realiza en la capa nativa, no en `TrustManager`.

```bash
strings -a lib/arm64-v8a/libnative-lib.so | grep -Ei 'ssl|verify|cert|pin|openssl'
```

## Análisis

La biblioteca usa OpenSSL o BoringSSL y una función de verificación que compara el certificado con una huella embebida. Los símbolos pueden estar ocultos; `nm`, `readelf` y Ghidra ayudan a localizar la llamada.

```bash
readelf -Ws libnative-lib.so | grep -Ei 'SSL|X509|verify'
```

## Explotación

1. Ejecutar un emulador API 29 o inferior con `frida-server`.
2. Hookear `SSL_CTX_set_cert_verify_callback` o la función de comparación para que devuelva éxito.
3. Instalar el certificado del proxy y redirigir el tráfico.
4. Iniciar sesión y capturar la respuesta.

```javascript
Interceptor.attach(Module.findExportByName('libssl.so', 'SSL_CTX_set_cert_verify_callback'), {
  onEnter: function (args) { args[1] = new NativeCallback(function () { return 1; }, 'int', ['pointer', 'pointer']); }
});
```

La flag aparece en la respuesta o en la pantalla de éxito.

## Evidencia

- Biblioteca y símbolos relevantes.
- Script de instrumentación.
- Petición y respuesta, con tokens redactados.
- Flag redactada.

## Lecciones aprendidas

- El pinning nativo no es inmune a la instrumentación.
- Hay que identificar la biblioteca TLS real, no solo las clases Java.
- Un emulador antiguo simplifica la carga de `frida-server`.

## Mitigaciones y detección

- Combinar pinning nativo con atestación y ofuscación.
- Verificar la integridad del APK y de las bibliotecas.
- Detectar Frida, hooks y proxies.
- No usar el cliente como única decisión de autenticación.

## Referencias

- <https://www.hackthebox.com/challenges/Anchored>
- <https://frida.re/docs/functions/>
- <https://www.openssl.org/docs/man3.0/man3/SSL_CTX_set_cert_verify_callback.html>
- <https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/>
