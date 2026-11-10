---
topic: smb-enumeration
tags: [smb, windows, enumeration, null-session]
---

# Enumeración SMB — sesión nula, shares y credenciales

[🇬🇧 English](smb-enumeration.en.md) | **Español**

> Nota reutilizable. No publicar salidas con credenciales reales.

## Idea

SMB (139/445) es el servicio que más información regala en Windows: nombres de equipo y dominio, shares, usuarios, políticas y, a veces, ficheros de configuración con contraseñas. La **sesión nula** (usuario vacío) y el **invitado** son los dos primeros intentos; si fallan, se prueba con credenciales ya obtenidas.

## Puertos y servicios

| Puerto | Servicio | Uso |
|---|---|---|
| 139/tcp | NetBIOS session | SMB sobre NetBIOS (legacy) |
| 445/tcp | SMB directo | Compartición de ficheros e IPC |
| 135/tcp | MSRPC | `rpcclient`, enumeración de usuarios |
| 389/636 | LDAP | Enumeración de AD si hay dominio |

## Enumeración sin credenciales

```bash
nmap -Pn -p 139,445 --script "smb-os-discovery,smb-enum-shares,smb-enum-users,smb2-security-mode" <IP>
smbclient -L //<IP> -N
smbclient //<IP>/<SHARE> -N
rpcclient -U '' -N <IP> -c 'enumdomusers'
nxc smb <IP> -u '' -p '' --shares
```

Qué se busca:

- **Shares no administrativos** (`backups`, `data`, `www`, `IT`): suelen tener configuración, backups y scripts.
- **Permisos de escritura**: un share escribible permite dejar un fichero que otro usuario ejecutará.
- **Sesión nula habilitada**: confirma una política laxa y abre `IPC$` para enumerar.
- **SMB signing deshabilitado**: habilita relay NTLM.

## Con credenciales

```bash
nxc smb <IP> -u <USER> -p '<PASS>' --shares --sessions --loggedon-users
smbclient //<IP>/<SHARE> -U '<DOMINIO>\<USER>%<PASS>'
smbmap -H <IP> -u <USER> -p '<PASS>' -R
```

Si la cuenta es administradora local, `nxc` lo marca (`Pwn3d!`) y se puede ejecutar con `psexec`, `wmiexec` o `smbexec`.

## Qué leer primero en un share

| Fichero | Qué contiene |
|---|---|
| `*.config`, `*.dtsConfig`, `web.config` | cadenas de conexión y contraseñas |
| `*.ps1`, `*.bat`, `*.vbs` | credenciales embebidas y rutas internas |
| `*.kdbx`, `*.psafe3` | bases de contraseñas (KeePass, Password Safe) |
| `unattend.xml`, `sysprep.inf` | contraseña de administrador en claro o base64 |
| `*.bak`, `*.zip`, `*.7z` | copias de bases y código fuente |
| `id_rsa`, `*.pem`, `*.pfx` | claves privadas y certificados |

## Ataques que salen de aquí

- **Password spraying** con la política descubierta (`nxc smb` contra una lista de usuarios).
- **Relay NTLM** si el signing está deshabilitado (`ntlmrelayx`).
- **Coerción** (`PetitPotam`, `PrinterBug`) para que el host se autentique contra nosotros.
- **Pass-the-hash** con el hash NTLM obtenido.

## Blindaje

- Deshabilitar SMBv1 y exigir **SMB signing** y cifrado.
- `RestrictAnonymous=1` y `EveryoneIncludesAnonymous=0`; retirar el acceso de invitado.
- Shares con permisos por grupo, sin escritura para `Everyone`.
- Contraseñas de servicio rotadas y sin secretos en ficheros de configuración.
- Segmentar 445/139 a la red de gestión.

## Detección

- Eventos 4624 tipo 3 con `ANONYMOUS LOGON` o `Administrator` desde estaciones no administrativas.
- Enumeración masiva de shares o usuarios (`rpcclient`, `enum4linux`) en poco tiempo.
- Accesos a `ADMIN$`/`C$` seguidos de creación de servicio (7045).
- Conexiones SMB salientes desde servidores que no deberían iniciarlas.

## Referencias

- <https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-security>
- <https://book.hacktricks.xyz/network-services-pentesting/pentesting-smb>
- <https://attack.mitre.org/techniques/T1021/002/>
