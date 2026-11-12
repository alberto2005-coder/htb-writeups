---
challenge: Free Services
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, email, phishing, eml, attachment, malware]
---

# Free Services — Hack The Box (Challenge)

[🌍 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

Se analiza un correo malicioso en formato `.eml`. Las cabeceras revelan el remitente real, la infraestructura y el cliente; el cuerpo contiene un enlace o adjunto codificado. Al extraer y decodificar el adjunto se obtiene el payload y la flag.

## Enunciado y superficie

- Forensics, Easy, retirado.
- Se entrega un `.eml` o un ZIP con el correo.
- El objetivo es identificar el ataque y extraer el indicador.

```bash
file suspicious.eml
head -40 suspicious.eml
```

## Reconocimiento

Se revisan las cabeceras `Received`, `From`, `Reply-To`, `Return-Path` y `Message-ID`. Se extraen URLs y adjuntos:

```bash
munpack suspicious.eml
exiftool suspicious.eml
```

## Análisis

El cuerpo puede estar en base64 o quoted-printable. Se decodifica y se revisan los enlaces con cuidado (sin visitarlos). Si hay adjunto, se calcula el hash y se inspecciona el tipo real:

```bash
base64 -d attachment.b64 > attachment.bin
file attachment.bin
sha256sum attachment.bin
```

Si el adjunto es un archivo comprimido o un documento con macros, se analiza en una VM aislada. La flag suele estar en el asunto, el nombre del adjunto o el contenido decodificado.

## Explicación del fallo

El correo confía en la apariencia del remitente y en un adjunto/enlace que el usuario puede abrir. La codificación MIME oculta el contenido real y las cabeceras pueden falsificarse.

## Reproducción local

1. Parsear el `.eml`.
2. Extraer y decodificar partes MIME.
3. Analizar URLs y adjuntos.
4. Localizar la flag y redactarla.

## Evidencia

- Cabeceras con dominios y direcciones redactados.
- Hash del adjunto.
- Contenido decodificado con la flag redactada.

## Lecciones aprendidas

- Las cabeceras `Received` ayudan a rastrear el origen.
- MIME base64/quoted-printable oculta el contenido.
- Los adjuntos deben analizarse en aislamiento.
- Un correo “gratuito” es un anzuelo clásico.

## Mitigación y detección

- Filtrado de correo y análisis de adjuntos.
- SPF, DKIM y DMARC.
- Bloquear macros y ejecutables.
- Formación contra phishing.

## Referencias

- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/free-services/>
- <https://www.rfc-editor.org/rfc/rfc5322>
- <https://attack.mitre.org/techniques/T1566/001/>
