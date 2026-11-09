---
challenge: Urgent
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, email, phishing, base64, vbscript]
type: Forensics
---


# Urgent — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags reales.

## TL;DR

Un correo de **phishing** en formato de mensaje completo. Hay que abrir la cabecera, decodificar las partes (`base64` y *quoted-printable*), resolver los enlaces con **URL encoding** y leer el adjunto, que es un **VBScript** con la descarga del siguiente stage.

## Enunciado y superficie

- Categoría Forensics; el reto entrega el material descrito en «Reconocimiento».

## Reconocimiento

- Superficie reducida a lo que entrega el enunciado; el detalle está en «Enunciado y superficie».

## Análisis del código

- El reto no entrega código fuente; el análisis se apoya en el comportamiento descrito en «Explicación del fallo».

## Explicación del fallo

Un correo de **phishing** en formato de mensaje completo. Hay que abrir la cabecera, decodificar las partes (`base64` y *quoted-printable*), resolver los enlaces con **URL encoding** y leer el adjunto, que es un **VBScript** con la descarga del siguiente stage.

## Reproducción local

- Reproduce el artefacto del reto en local (intérprete o contenedor) para iterar sin el servidor.

## Explotación

- Ver las secciones adyacentes para el detalle.

## Evidencia

- Un mensaje de correo (`.eml`).

## Lecciones aprendidas

- **Abrirlo en el cliente**: nunca; analizar el `.eml` en texto evita ejecutar nada.
- **Cuerpo en varias partes**: recorrer todas, no sólo la primera.
- **Codificación del asunto**: `=?UTF-8?B?...?=` se decodifica con `email.header`.

- Un `.eml` es un contenedor con capas: cabecera, partes codificadas y adjuntos.
- El URL encoding es ofuscación, no protección; un `unquote` lo deshace.
- Un VBScript adjunto que descarga un ejecutable es la cadena clásica de phishing.

## Mitigaciones y detección

- Aplicar la corrección de la categoría: validación en servidor, versiones parcheadas y mínimo privilegio.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

- [rop-stack](../../knowledge/pwn/rop-stack.md)
- [phishing-infrastructure](../../knowledge/osint/phishing-infrastructure.md)

## Método

1. **Cabecera**: remitente real, `Return-Path`, servidor de salida y asunto.

```bash
grep -iE '^(From|Return-Path|Received|Subject|Date):' mail.eml
```

2. **Cuerpo**: el mensaje suele ser `multipart/alternative`; el HTML va en base64 o *quoted-printable*.

```bash
python3 -c "import email,sys; m=email.message_from_file(open('mail.eml')); [print(p.get_payload(decode=True).decode('utf-8','replace')) for p in m.walk() if p.get_content_type()=='text/html']"
```

3. **Enlaces**: resolver los `%xx` y desconfiar de los acortadores y de dominios con caracteres parecidos.

```bash
python3 -c "import urllib.parse,sys; print(urllib.parse.unquote(sys.argv[1]))" '<url>'
```

4. **Adjunto**: un `.vbs`/`.js` con `WScript.Shell` o `MSXML2.XMLHTTP` indica descarga y ejecución. Los literales del script (y sus variables) dan la URL del payload y el nombre del fichero que deja.

5. **IOC**: remitente, asunto, URL del payload y hash del adjunto.
