---
machine: DarkCorp
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, active-directory, roundcube, postgresql, ntlm-relay, adidns, shadow-credentials, sssd, gpo]
---

# DarkCorp — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Tres hosts: un Debian con web y correo, un servidor web Windows y un DC. Un XSS en RoundCube roba correos del admin y revela un subdominio; un reset y una SQLi en PostgreSQL dan RCE. Un backup PGP crackeado da acceso al dominio; desde WEB-01 se relaya NTLM a LDAP, se crea un registro ADIDNS, se usa PrinterBug y se obtiene un silver ticket. La cadena sigue con credenciales en tareas, DPAPI, spray, shadow credentials, UPN spoofing, caché SSSD y abuso de GPO hasta Domain Admin.

## Reconocimiento

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `drip.htb` es un Debian con nginx, SSH y correo.
- `ffuf` descubre `mail.drip.htb` y el panel de administración.
- El entorno incluye `WEB-01` y `DC-01` en la red interna.

## Enumeración

- RoundCube es vulnerable a CVE-2024-42009: un correo con XSS se ejecuta al abrirlo.
- Se envía el payload al admin `bcase` y se exfiltra su correo, que revela el subdominio del dashboard.
- El reset de contraseña y una SQLi en el login permiten entrar al panel.

## Foothold

La SQLi confirma PostgreSQL. Con permisos de superusuario se usa `COPY ... TO PROGRAM` o `archive_command` para ejecutar comandos y obtener una shell como `postgres`.

```sql
COPY (SELECT '') TO PROGRAM 'id';
```

## Movimiento lateral

Un backup PGP contiene el hash de `ebelford`; se crackea y se usa por SSH. Esa cuenta también accede al portal de estado de `WEB-01`, que realiza comprobaciones y autenticaciones NTLM.

- Se relaya NTLM a LDAP como `svc_acc`, miembro de `DNSADMINS`.
- Se crea un registro ADIDNS para `DC-01` apuntando al atacante.
- PrinterBug fuerza a `WEB-01` a autenticarse; el relay permite un silver ticket de Administrator en `WEB-01`.

## Escalada de privilegios

En `WEB-01` se recuperan credenciales de una tarea programada y se descifra una credencial DPAPI. El spray obtiene otra cuenta, que puede pedir shadow credentials sobre un usuario con cuenta `.adm`; un UPN spoofing devuelve acceso de admin en `drip`. Desde root en `drip` se leen credenciales cacheadas de SSSD y se pivota al DC. El usuario final modifica una GPO y se convierte en Domain Admin.

## Evidencia

- RoundCube CVE-2024-42009 y correo del admin.
- SQLi PostgreSQL y RCE.
- Hash de `ebelford` y acceso SSH.
- Relay NTLM, ADIDNS, PrinterBug y silver ticket.
- Tareas, DPAPI, spray, shadow credentials, UPN spoofing, SSSD y GPO.

## Lecciones aprendidas

- Un XSS en webmail puede exponer el resto de la cadena.
- PostgreSQL con superusuario permite RCE por varias vías.
- Los backups y perfiles de correo filtran hashes reutilizables.
- En AD, la clave está en encadenar relay, DNS, tickets y credenciales cacheadas.

## Mitigación y detección

- Actualizar RoundCube y escapar el cuerpo de los mensajes.
- Restringir superusuario de PostgreSQL y `COPY PROGRAM`.
- Firmar LDAP/SMB, deshabilitar NTLM y proteger ADIDNS.
- Auditar tareas, DPAPI, GPO, UPN y caché SSSD; rotar credenciales.

## Referencias

- [0xdf — DarkCorp](https://0xdf.gitlab.io/2025/10/18/htb-darkcorp.html)
- [IppSec — DarkCorp](https://www.youtube.com/watch?v=miOE_yYh1JY)
- [Hack The Box — DarkCorp](https://app.hackthebox.com/machines/darkcorp)
