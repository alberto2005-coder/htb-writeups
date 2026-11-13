---
sherlock: HookFlare
category: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, android, smishing, banking-trojan, aes-ecb, discord-webhook]
---

# HookFlare — Hack The Box (Sherlock)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Una campaña de smishing distribuye un troyano bancario para Android. Se analiza el APK, la interceptación de SMS y la exfiltración cifrada hacia un webhook de Discord.

## Evidencias

- APK sospechoso y permisos declarados.
- Exportación de SMS y registros de llamadas.
- Captura de red o logs de C2.
- Cadenas y configuración embebida en el APK.

```bash
sha256sum sample.apk
apktool d sample.apk -o apk
```

## Investigación

### 1. Análisis estático

Se revisan `AndroidManifest.xml`, receptores de SMS, servicios en segundo plano y permisos. Un receptor con `RECEIVE_SMS` y un servicio de accesibilidad sugiere interceptación y control de la interfaz.

```bash
jadx -d jadx sample.apk
grep -RInE 'Discord|webhook|AES|ECB|sms|otp' jadx/sources | head
```

### 2. Flujo de phishing y 2FA

El mensaje SMS contiene un enlace que descarga el APK. La aplicación solicita permisos de SMS y accesibilidad, intercepta el código de un solo uso y lo reenvía. Se reconstruye el orden: recepción, instalación, concesión de permisos y primer C2.

### 3. Cifrado y exfiltración

Las cadenas revelan una clave AES y modo ECB. ECB cifra bloques iguales de forma idéntica, por lo que los datos estructurados filtran patrones. El destino es un webhook de Discord, que actúa como canal de exfiltración.

```bash
strings -a sample.apk | grep -Ei 'https://discord|webhook|key'
```

## Conclusiones

- Número y dominio de la campaña.
- Permisos y componentes Android abusados.
- Formato de cifrado y canal de salida.
- IOCs: hashes, dominios y webhooks, redactados.

## Lecciones

- Los permisos de accesibilidad y SMS son combinaciones de alto riesgo.
- ECB no oculta la estructura de los datos.
- Un webhook legítimo puede servir como C2 y exfiltración.

## Referencias

- <https://www.hackthebox.com/sherlocks/HookFlare>
- <https://attack.mitre.org/techniques/T1417/>
- <https://attack.mitre.org/techniques/T1636/>
- <https://developer.android.com/guide/topics/manifest/uses-permission-element>
