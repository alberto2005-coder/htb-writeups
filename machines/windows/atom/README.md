---
machine: Atom
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, smb, electron, updater, redis]
---

# Atom — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un recurso SMB de actualizaciones es escribible y la aplicación Electron confía en el manifiesto de `electron-updater`. Se publica una actualización maliciosa y se obtiene ejecución; Redis guarda la configuración de PortableKanban con la contraseña del administrador.

## Reconocimiento

```bash
nmap -Pn -sCV -p80,445,6379 <IP>
smbclient -N -L //<IP>
smbclient -N //<IP>/Software_Updates
# Reemplazar latest.yml y el paquete por un payload
redis-cli -h <IP> -p 6379
keys *
get <CLAVE>
```

## Enumeración

- SMB expone `Software_Updates` con permisos de escritura.
- La app Electron consulta un `latest.yml` y descarga el paquete.
- Redis en `6379` contiene claves de PortableKanban.

## Acceso inicial

Se reemplaza el manifiesto y el paquete de la actualización por un ejecutable controlado. La aplicación lo descarga y ejecuta sin validar la firma del publicador, lo que da una sesión como el usuario que abrió Atom.

## Escalada de privilegios

Redis contiene el archivo de PortableKanban con la contraseña del administrador cifrada. Se recupera la clave, se descifra y se usa para acceder por WinRM o SMB como Administrator.

## Evidencia

- `latest.yml` modificado en el recurso SMB.
- Proceso hijo del actualizador ejecutando el payload.
- Clave de PortableKanban descifrada y acceso administrativo.

## Lecciones aprendidas

- Un canal de actualización escribible es ejecución de código.
- La firma del paquete debe validarse en el cliente y en el servidor.
- Redis sin autenticación expone secretos de aplicaciones de escritorio.

## Mitigación y detección

- Restringir la escritura en el recurso de actualizaciones y firmar los paquetes.
- Exigir TLS y validar el manifiesto antes de descargar.
- Proteger Redis y no guardar contraseñas recuperables.

## Referencias

- [0xdf — Atom](https://0xdf.gitlab.io/2021/07/10/htb-atom.html)
- [Electron — autoUpdater](https://www.electronjs.org/docs/latest/api/auto-updater)
- [Hack The Box — Atom](https://app.hackthebox.com/machines/atom)
