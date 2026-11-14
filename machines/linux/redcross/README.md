---
machine: RedCross
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, xss, haraka, postgresql, nss, bof, rop]
---

# RedCross — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un portal con varios vhosts permite obtener una cookie de administrador por XSS o por el propio flujo de registro. Desde el panel se abre el firewall y se llega a Haraka, vulnerable a RCE, o se usa la gestión de usuarios para inyectar en PostgreSQL y crear una cuenta del jail. Con `penelope`, hay tres rutas a root: un usuario con gid de sudoers, las credenciales de `unixnssroot` o un buffer overflow en `iptctl`.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,443 <IP>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u https://<DOMAIN> -H "Host: FUZZ.<DOMAIN>" -k
```

## Enumeración

- `intra.redcross.htb` tiene un formulario de contacto y `admin.redcross.htb` un panel de administración.
- El panel permite abrir el firewall y gestionar usuarios del jail.
- Haraka en el 25 y PostgreSQL en localhost completan la superficie.

## Acceso inicial

La XSS en el formulario de contacto roba la cookie del administrador; alternativamente, el registro devuelve una cookie válida. Con acceso al panel se abre el puerto 25 y se explota Haraka para obtener una shell, o se usa la inyección SQL de gestión de usuarios para crear una cuenta con acceso al jail y entrar como `penelope`.

## Escalada de privilegios

Ruta 1: insertar un usuario con gid 27 (sudo) y ejecutar `sudo su`. Ruta 2: leer `/etc/nss-pgsql-root.conf`, conectarse como `unixnssroot` e insertar un usuario con uid 0. Ruta 3: el SUID `iptctl` copia la acción con `strcpy` y desborda la pila; con ROP se llama a `execvp` para lanzar una shell.

## Evidencia

- Cookie de administrador y acceso al panel.
- Cuenta creada en PostgreSQL y shell como `penelope`.
- Usuario con uid/gid privilegiado o ROP en `iptctl`.

## Lecciones aprendidas

- Un jail basado en NSS hereda los fallos de la base que lo alimenta.
- Las cookies de sesión y los formularios de contacto son una puerta al panel.
- Los SUID con buffers fijos siguen siendo relevantes.

## Mitigación y detección

- Migrar el jail a un mecanismo con privilegios mínimos y auditoría.
- Sanitizar la XSS y usar cookies HttpOnly/SameSite.
- Compilar con stack protector, ASLR y sin SUID innecesarios.

## Referencias

- [0xdf — RedCross](https://0xdf.gitlab.io/2019/04/13/htb-redcross.html)
- [IppSec — RedCross](https://www.youtube.com/watch?v=-GNyDEQ9UDU)
- [Hack The Box — RedCross](https://app.hackthebox.com/machines/redcross)
