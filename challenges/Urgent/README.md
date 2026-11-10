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

El artefacto es un mensaje completo en formato `.eml`. Se analiza como texto: cabeceras (`From`, `Reply-To`, `Received`), estructura MIME y partes codificadas. Nunca se abre en un cliente de correo.

## Análisis del código

No hay código de aplicación, pero sí un **adjunto ejecutable**: un `.vbs` que descarga el siguiente stage. El `.eml` es el contenedor; el «código» a leer es el script adjunto y las URLs que aparecen en él.

## Explicación del fallo

Un correo de **phishing** en formato de mensaje completo. Hay que abrir la cabecera, decodificar las partes (`base64` y *quoted-printable*), resolver los enlaces con **URL encoding** y leer el adjunto, que es un **VBScript** con la descarga del siguiente stage.

## Reproducción local

```bash
python3 - <<'PY'
from email import policy
from email.parser import BytesParser
msg = BytesParser(policy=policy.default).parse(open('sample.eml','rb'))
print(msg['From'], msg['Reply-To'], msg['Subject'])
for part in msg.walk():
    print(part.get_content_type(), part.get_filename())
    if part.get_filename():
        open(part.get_filename(),'wb').write(part.get_payload(decode=True))
PY
unzip -l sample.eml 2>/dev/null; cat *.vbs
```

El cuerpo puede venir en `base64` o *quoted-printable*; `get_payload(decode=True)` se encarga de ambas. Las URLs del VBS suelen estar en **URL encoding** (`%2F`, `%3A`): `urllib.parse.unquote` las resuelve.

## Explotación

1. Se decodifican las partes MIME del `.eml` (`base64`/`quoted-printable`).
2. Se resuelven las URLs con `urllib.parse.unquote`.
3. Se lee el `.vbs` adjunto: `WScript.Shell`/`MSXML2.XMLHTTP` descargan el siguiente stage y dejan el nombre del fichero que se escribe en disco.

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

- Bloquear adjuntos ejecutables (`.vbs`, `.js`, `.hta`, `.lnk`) y aplicar ASR/lista blanca de aplicaciones.
- Autenticación de correo (SPF, DKIM, DMARC) y análisis de `Received` para detectar suplantación.
- Formación: un dominio con `Reply-To` distinto del `From` y prisa en el asunto son señales.
- Detección: `wscript.exe` hijo de un cliente de correo y descargas HTTP desde un script de Windows.

- Correlacionar `Received`, `Message-ID` y el hash del adjunto para atribuir la campaña y bloquear el remitente.
- Detección: revisar los logs de la aplicación y alertar de 4xx/5xx repetidos o entradas anómalas.

## Referencias

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
