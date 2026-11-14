---
topic: Impresoras y PJL
tags: [hardware, printer, pjl, pret, filesystem, base64]
---

# Impresoras y PJL

[🌐 English](printer-pjl.en.md) | **Español**

## Concept

PJL (Printer Job Language) es un lenguaje de control usado por impresoras HP y compatibles. Permite consultar el estado, cambiar ajustes y acceder a un sistema de archivos interno. Si el puerto de impresión está expuesto sin autenticación, se pueden listar y descargar trabajos, fuentes y configuraciones.

## Cuándo aplica

- Impresoras en red con el puerto 9100 abierto.
- Paneles de administración con credenciales por defecto.
- Trabajos retenidos en `saveDevice` o `spool`.
- Retos de hardware con un servicio de impresión.

## Procedimiento

1. Identificar el servicio y el banner.
2. Conectar con PRET en modo PJL.
3. Listar el sistema de archivos y navegar.
4. Descargar el archivo de interés.
5. Decodificar si el contenido está en base64.

```bash
nmap -Pn -sV -p 9100 <IP>
python2.7 pret.py <IP>:9100 pjl
```

## Variantes

- `FSUPLOAD`/`FSDOWNLOAD` para leer o escribir archivos.
- `FSDIRLIST` para enumerar directorios.
- Trabajos en `saveDevice/SavedJobs/InProgress`.
- PDF o documentos codificados en base64.
- PostScript o FTP expuestos en el mismo dispositivo.

## Limitaciones

- PJL puede estar deshabilitado o filtrado.
- Algunos modelos requieren autenticación para el filesystem.
- PRET depende de Python 2.7.
- El firmware moderno limita comandos peligrosos.

## Mitigación y detección

- Deshabilitar PJL y puertos no usados.
- Segmentar impresoras en una VLAN y restringir por IP.
- Cambiar credenciales y borrar trabajos retenidos.
- Alertar de comandos PJL, descargas de `saveDevice` y accesos anómalos al puerto 9100.

## Referencias

- <https://github.com/RUB-NDS/PRET>
- <https://hacking-printers.net/wiki/index.php/Printer_Security_Testing_Cheat_Sheet>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1005/>
