---
challenge: Pinned
type: Mobile
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [mobile, android, certificate-pinning, frida, okhttp, interception]
---

# Pinned — Hack The Box (Challenge)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

La app usa certificate pinning y solo permite el login automático. El pin se aplica en el cliente, así que un hook de Frida sobre `TrustManager` y `CertificatePinner` elimina la validación. Al interceptar el tráfico se recupera la credencial y la flag.

## Enunciado y superficie

- Mobile, Medium, retirado.
- Se entrega `pinned.apk` y un `README.txt`.
- La app requiere Android 10 o inferior para instalar el APK.

```bash
apktool d pinned.apk -o pinned
jadx -d jadx pinned.apk
```

## Reconocimiento

- `AndroidManifest.xml` declara `usesCleartextTraffic` y una actividad de login.
- `jadx` muestra OkHttp y una clase con `CertificatePinner`.
- El pin compara el certificado del servidor con un hash embebido.

```bash
grep -RInE 'CertificatePinner|TrustManager|sha256/|pin' jadx/sources | head -n 30
```

## Análisis

El pinning se implementa en dos capas: el `TrustManager` personalizado y el `CertificatePinner` de OkHttp. Bloquear solo una deja la otra activa. Un hook de Frida puede sustituir ambas por validaciones permisivas.

```javascript
Java.perform(function () {
  var Pinner = Java.use('okhttp3.CertificatePinner');
  Pinner.check.overload('java.lang.String', 'java.util.List').implementation = function () {};
});
```

## Explotación

1. Arrancar un emulador API 29 o inferior con `frida-server`.
2. Ejecutar la app con el script de bypass.
3. Configurar un proxy e instalar el certificado de Burp o mitmproxy.
4. Iniciar sesión y capturar la petición.

```bash
frida -U -f <PACKAGE> -l bypass.js --no-pause
```

La respuesta de login contiene la flag o una credencial que permite obtenerla.

## Evidencia

- Clase de pinning y script de bypass.
- Petición y respuesta interceptadas, con tokens redactados.
- Pantalla de éxito, con la flag redactada.

## Lecciones aprendidas

- El pinning en cliente no impide el análisis dinámico.
- Hay que desactivar todas las capas de validación, no solo una.
- Un emulador con una versión antigua de Android facilita la instrumentación.

## Mitigaciones y detección

- Combinar pinning con atestación y ofuscación.
- No confiar en el cliente para decidir el éxito del login.
- Detectar Frida, proxies y certificados de usuario.
- Rotar pins y monitorizar errores de validación.

## Referencias

- <https://www.hackthebox.com/challenges/Pinned>
- <https://frida.re/docs/android/>
- <https://square.github.io/okhttp/features/https/>
- <https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/>
