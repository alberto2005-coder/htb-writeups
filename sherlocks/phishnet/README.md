---
sherlock: PhishNet
category: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [soc, phishing, email-headers, spf, base64, zip]
---

# PhishNet — Hack The Box (Sherlock)

[🌐 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha metodológica; sin respuestas literales ni datos reales.

## Escenario

Un usuario reporta un correo sospechoso. Se pide confirmar el origen, comprobar la autenticación del dominio remitente, analizar el adjunto y extraer indicadores para bloquear la campaña.

## Evidencias

- Mensaje original en formato `.eml`, con cabeceras completas.
- Adjunto codificado en base64 dentro del mensaje.
- Registros DNS públicos del dominio remitente.
- Hashes calculados sobre el mensaje y el adjunto.

```bash
sha256sum <EVIDENCE>.eml
```

## Investigación

### 1. Cabeceras y cadena de entrega

Se leen las cabeceras `Received` de abajo arriba para reconstruir la ruta. Se comparan `Return-Path`, `From`, `Reply-To` y `Message-ID`; las discrepancias suelen revelar una suplantación.

```bash
grep -iE '^(Received|From|Return-Path|Reply-To|Message-ID|Authentication-Results):' message.eml
```

Se valida SPF contra la IP de origen, DKIM contra el selector y DMARC contra el dominio alineado. Un fallo de SPF no demuestra por sí solo el phishing, pero junto con la discrepancia de dominios es evidencia fuerte.

### 2. Adjunto

El adjunto se decodifica desde base64 y se identifica por magic bytes, no por extensión. Se calcula SHA-256 y se inspecciona el ZIP sin extraerlo.

```bash
base64 -d attachment.b64 > attachment.bin
file attachment.bin
7z l attachment.bin
sha256sum attachment.bin
```

### 3. Contenido y persistencia

Dentro del ZIP se revisan nombres, fechas y cualquier ejecutable, LNK o documento con macros. Los nombres con doble extensión y las rutas de extracción son indicadores habituales. Se mapea el flujo a MITRE T1566.001.

## Conclusiones

- Dominio e IP reales del remitente.
- Resultado de SPF, DKIM y DMARC.
- Naturaleza del adjunto y hashes, redactados.
- Acción recomendada: bloquear remitente, dominio e IOC de red.

## Lecciones

- La extensión visible no determina el tipo de archivo.
- SPF, DKIM y DMARC se interpretan juntos, no por separado.
- Un ZIP aparentemente inocuo puede contener un LNK o un ejecutable.

## Referencias

- <https://www.hackthebox.com/sherlocks/PhishNet>
- <https://attack.mitre.org/techniques/T1566/001/>
- <https://datatracker.ietf.org/doc/html/rfc7208>
- <https://learn.microsoft.com/en-us/microsoft-365/security/office-365-security/email-authentication-dmarc-configure>
