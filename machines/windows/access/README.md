---
machine: Access
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, ftp, mdb, outlook, telnet, runas, dpapi]
---

# Access — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

FTP anónimo entrega `backup.mdb` y un ZIP protegido. La base Microsoft Access contiene la contraseña de `engineer`, que abre el ZIP y revela un PST de Outlook con la contraseña de `security`; telnet permite entrar. En el host, `cmdkey /list` muestra credenciales cacheadas de Administrator y `runas /savecred` ejecuta una reverse shell con esos privilegios.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p21,23,80 <IP>
ftp -a <IP>
```

## Enumeración

- IIS en el 80, FTP anónimo en el 21 y telnet en el 23.
- `Backups/backup.mdb` y `Engineer/Access Control.zip` son accesibles.
- La base contiene la tabla `auth_user` con credenciales.

## Acceso inicial

Se descarga el MDB y se exporta `auth_user` con `mdb-export`; la contraseña de `engineer` abre el ZIP, que contiene `Access Control.pst`. Al leer el correo se obtiene la contraseña de `security`, válida en telnet, y se consigue una shell.

## Escalada de privilegios

`cmdkey /list` revela credenciales de Administrator guardadas. Se sube una reverse shell de Nishang y se ejecuta con `runas /savecred /user:ACCESS\Administrator`, heredando las credenciales cacheadas. Como alternativa, se extraen el master key y el archivo de credenciales DPAPI y se descifran fuera del host.

## Evidencia

- Listado FTP con los dos archivos.
- Salida de `mdb-export` y correo del PST.
- `cmdkey /list` y shell como Administrator.

## Lecciones aprendidas

- Un backup de base de datos puede contener credenciales de varios sistemas.
- Los archivos PST y los correos son una fuente clásica de secretos.
- Las credenciales cacheadas de Windows permiten movimiento lateral sin conocer la contraseña.

## Mitigación y detección

- Deshabilitar FTP anónimo y telnet; usar SFTP/SSH.
- Proteger backups y buzones con cifrado y permisos mínimos.
- Limpiar Credential Manager y aplicar LAPS a las cuentas locales.

## Referencias

- [0xdf — Access](https://0xdf.gitlab.io/2019/03/02/htb-access.html)
- [IppSec — Access](https://www.youtube.com/watch?v=Rr6Oxrj2IjU)
- [Hack The Box — Access](https://app.hackthebox.com/machines/access)
