---
sherlock: Anpu
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, android, apk, trojan, overlay, ransomware]
---

# Anpu — Hack The Box (Sherlock)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un usuario de Android instala una aplicación fuera de la tienda oficial. Días después aparece una pantalla de rescate y contactos reciben mensajes. Se entrega el APK, una captura y logs del dispositivo.

## Evidencias

- `sample.apk` y su manifiesto.
- Captura de la pantalla de rescate.
- Logcat y tráfico de red.

```bash
sha256sum sample.apk
apktool d sample.apk -o apk
```

## Investigación

### 1. Análisis estático

Se revisan permisos, receptores y servicios. Permisos de accesibilidad, superposición y SMS son señales de un troyano bancario o ransomware.

```bash
jadx -d jadx sample.apk
grep -R "AccessibilityService\|SYSTEM_ALERT_WINDOW" apk/AndroidManifest.xml
```

### 2. Cadenas y configuración

Se buscan URLs, claves y nombres de paquetes. El APK puede descargar una segunda etapa; se identifican dominios y el formato de la configuración.

```bash
strings sample.apk | grep -E 'https?://'
```

### 3. Comportamiento

Logcat y el PCAP muestran la persistencia, el cifrado de archivos y la exfiltración. La pantalla de rescate se superpone a la app legítima para capturar credenciales.

## Conclusiones

- El APK abusa de accesibilidad y superposición.
- La segunda etapa se descarga desde un dominio identificable.
- El ransomware cifra archivos y muestra una pantalla de rescate.
- Los permisos excesivos son la primera alerta.

## Lecciones

- Un APK es analizable sin ejecutarlo.
- Los permisos revelan capacidades antes que el código.
- La segunda etapa puede estar en el mismo servidor.
- El análisis móvil combina estático y dinámico.

## Referencias

- <https://www.hackthebox.com/sherlocks>
- <https://owasp.org/www-project-mobile-app-security/>
- <https://attack.mitre.org/techniques/T1417/>
