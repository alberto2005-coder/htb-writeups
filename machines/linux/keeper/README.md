---
machine: Keeper
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, request-tracker, default-creds, keepass, cve-2023-32784, ssh]
---

# Keeper — Hack The Box (Linux)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Request Tracker 4.4.4 en `tickets.keeper.htb` conserva las credenciales por defecto. Un ticket contiene la contraseña inicial de `lnorgaard`, válida por SSH. En su home hay un volcado de memoria de KeePass y la base `.kdbx`; CVE-2023-32784 recupera la contraseña maestra y dentro está la clave privada de root.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

El puerto 80 redirige a `tickets.keeper.htb`. Se añade al hosts:

```bash
echo '<IP> tickets.keeper.htb keeper.htb' | sudo tee -a /etc/hosts
```

La aplicación es Request Tracker 4.4.4.

## Acceso inicial

Se prueban las credenciales documentadas de RT (`root` y la contraseña por defecto). En `Admin → Users` hay un ticket/comentario con la contraseña inicial de `lnorgaard`. Se reutiliza por SSH:

```bash
ssh lnorgaard@<IP>
```

## Escalada a root

En `/home/lnorgaard` hay un ZIP con `KeePassDumpFull.dmp` y `passcodes.kdbx`. CVE-2023-32784 permite recuperar la contraseña maestra del volcado:

```bash
python3 keepass_dump.py KeePassDumpFull.dmp
kpcli --kdb passcodes.kdbx
```

Dentro de la base está la clave privada de root en formato PuTTY. Se convierte y se usa:

```bash
puttygen root.ppk -O private-openssh -o root.id_rsa
chmod 600 root.id_rsa
ssh -i root.id_rsa root@<IP>
```

## Evidencia

- Login en RT y ticket con contraseña redactada.
- `KeePassDumpFull.dmp` y `passcodes.kdbx`.
- Contraseña maestra recuperada y clave de root redactadas.

## Lecciones aprendidas

- Las credenciales por defecto de RT siguen apareciendo en producción.
- Los tickets pueden contener secretos en texto claro.
- Los volcados de memoria de KeePass filtran la contraseña maestra.
- Una clave de root en una bóveda compartida cierra la cadena.

## Mitigación y detección

- Cambiar credenciales por defecto y aplicar MFA.
- No guardar contraseñas en tickets/comentarios.
- Actualizar KeePass y restringir volcados de proceso.
- Detectar acceso a `KeePassDumpFull.dmp` y `kpcli`.

## Referencias

- <https://nvd.nist.gov/vuln/detail/CVE-2023-32784>
- <https://www.hackthebox.com/machines/keeper>
- <https://bestpractical.com/request-tracker>
