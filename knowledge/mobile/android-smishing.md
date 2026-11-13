---
topic: Android smishing
tags: [mobile, android, smishing, sms, accessibility, overlay, otp]
---

# Android smishing

[🌐 English](android-smishing.en.md) | **Español**

## Concepto

El smishing combina un mensaje de texto con un enlace o APK malicioso. El troyano resultante pide permisos de SMS y accesibilidad para interceptar OTP, mostrar overlays y exfiltrar datos. El análisis une el mensaje, el APK y la infraestructura de C2.

## Cuándo aplica

- Campaña de mensajes con enlace a una APK.
- Robo de códigos 2FA.
- Permisos de accesibilidad o `SYSTEM_ALERT_WINDOW`.
- Exfiltración a un webhook o servidor remoto.

## Procedimiento

1. Preservar el SMS, el remitente y el enlace.
2. Analizar el APK y su manifiesto.
3. Revisar receptores de SMS y servicios de accesibilidad.
4. Buscar URLs, webhooks y claves embebidas.
5. Correlacionar con tráfico de red y cuentas afectadas.

```bash
apktool d sample.apk -o apk
grep -RInE 'RECEIVE_SMS|READ_SMS|BIND_ACCESSIBILITY|SYSTEM_ALERT_WINDOW' apk/AndroidManifest.xml
jadx -d jadx sample.apk
grep -RInE 'Discord|webhook|otp|AES|ECB' jadx/sources | head
```

## Variantes

- Enlace a una APK fuera de la tienda oficial.
- Overlay sobre la app bancaria.
- Interceptación de SMS y reenvío.
- Exfiltración cifrada con AES-ECB.

## Limitaciones

- Los mensajes pueden borrarse.
- El APK puede descargarse tras la instalación.
- Los permisos pueden concederse manualmente.
- El C2 puede estar inactivo durante el análisis.

## Mitigación y detección

- Bloquear APKs de fuentes desconocidas.
- Restringir accesibilidad y permisos de SMS.
- Monitorizar webhooks y dominios recién registrados.
- Alertar de instalaciones fuera de la tienda y OTP leídos.

## Referencias

- <https://attack.mitre.org/techniques/T1660/>
- <https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/>
- <https://www.ncsc.gov.uk/collection/mobile-device-guidance>
