---
topic: Android certificate pinning
tags: [mobile, android, certificate-pinning, frida, okhttp, tls]
---

# Android certificate pinning

[🌐 English](android-certificate-pinning.en.md) | **Español**

## Concepto

El certificate pinning exige que el certificado o la clave pública del servidor coincida con un valor conocido. En Android se implementa en Java/Kotlin (`TrustManager`, OkHttp `CertificatePinner`) o en una biblioteca nativa con OpenSSL/BoringSSL. Impide aceptar cualquier CA del almacén del dispositivo, pero no impide instrumentar el proceso.

## Cuándo aplica

- Interceptación de tráfico de una app móvil.
- Análisis de una API que falla con el certificado del proxy.
- Revisión de defensas en cliente.
- Retos con `pinning`, `anchoring` o `network security config`.

## Requisitos y condiciones

- APK o app instalada en un emulador controlado.
- Proxy con CA propia.
- Frida o un entorno de parcheo.
- Capacidad de reiniciar la app y de modificar su configuración de red.

## Procedimiento

1. Descompilar y buscar `CertificatePinner`, `TrustManager` y `network_security_config`.
2. Revisar bibliotecas nativas con `strings`, `readelf` y Ghidra.
3. Instalar la CA del proxy en el dispositivo.
4. Hookear todas las capas de validación, no solo una.
5. Verificar que la petición llega al proxy y que la respuesta se procesa.

```javascript
Java.perform(function () {
  var Pinner = Java.use('okhttp3.CertificatePinner');
  Pinner.check.overload('java.lang.String', 'java.util.List').implementation = function () {};
});
```

## Variantes

- Pin de certificado hoja o de clave pública.
- Pin en `network_security_config.xml`.
- Pin nativo con `SSL_CTX_set_cert_verify_callback`.
- Pinning combinado con atestación y ofuscación.

## Limitaciones

- Un pin en cliente siempre puede desactivarse con instrumentación.
- Hookear solo OkHttp deja activo el `TrustManager` o la capa nativa.
- Algunas apps detectan Frida, proxies o certificados de usuario.
- Un emulador antiguo puede no reproducir el comportamiento real.

## Mitigación

- Combinar pinning con atestación de integridad.
- Ofuscar y dispersar las comprobaciones.
- No usar el cliente como única decisión de autenticación.
- Rotar pins y monitorizar fallos de validación.

## Detección

- Alertar de errores TLS repetidos desde una misma cuenta.
- Detectar proxies, CA de usuario y procesos de instrumentación.
- Comparar la huella del APK con la versión publicada.
- Revisar telemetría de integridad y de atestación.

## Referencias

- <https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/>
- <https://square.github.io/okhttp/features/https/>
- <https://frida.re/docs/android/>
- <https://developer.android.com/privacy-and-security/security-config>
