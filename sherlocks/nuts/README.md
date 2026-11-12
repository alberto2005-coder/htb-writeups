---
sherlock: Nuts
difficulty: Medium
category: DFIR
platform: Hack The Box
state: Unverified
tags: [dfir, windows, nuget, supply-chain, powershell, defender, prefetch]
---

# Nuts — Hack The Box Sherlock

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Pendiente de confirmar en HTB sin sesión; ficha de referencia no jugada.
> Sin flags, hashes ni dominios reales.

## TL;DR

El caso gira alrededor de un equipo Windows con más de 300.000 ficheros y un paquete NuGet malicioso. El paquete imita el nombre de uno legítimo (`PublishIgnor` frente a `PublishIgnore`) y ejecuta `init.ps1` durante la restauración. El script descarga una carga, crea persistencia y toca Defender. La evidencia está repartida entre la caché `.nuget`, el historial de PowerShell, Prefetch, tareas programadas y los eventos del antivirus.

## Punto de partida

```powershell
Get-ChildItem C:\Users -Directory
Get-ChildItem C:\Users\<USER>\.nuget\packages -Directory | Measure-Object
Get-ChildItem C:\Users\<USER>\.nuget\packages -Directory | Where-Object Name -match 'publish'
```

Con cientos de miles de rutas, no se lanza un `Get-ChildItem -Recurse` global. Se acota por usuario, por fecha y por extensión. `Everything` o `rg` sobre rutas concretas son más rápidos que PowerShell recursivo.

## 1. El paquete NuGet

```powershell
Get-ChildItem C:\Users\<USER>\.nuget\packages\publishignor -Recurse |
  Select-Object FullName,Length,LastWriteTime
Get-Content C:\Users\<USER>\.nuget\packages\publishignor\<VERSION>\tools\init.ps1
```

Señales:

- Nombre a una letra del paquete legítimo (typosquatting).
- Versión muy reciente y editor distinto.
- `init.ps1`, `install.ps1` o `tools/` con descarga y ejecución.
- URL de descarga ofuscada, `Invoke-WebRequest`, `FromBase64String` o `iex`.
- Fichero `.nupkg` con el mismo hash en otros equipos.

El script se guarda como evidencia y se extraen las URLs como `<C2_HOST>`.

## 2. Historial de PowerShell

```powershell
Get-Content C:\Users\<USER>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

Se buscan:

```text
dotnet add package PublishIgnor
Install-Package PublishIgnor
nuget install PublishIgnor
```

El historial confirma que el usuario instaló el paquete y en qué directorio. También puede mostrar los comandos de persistencia ejecutados después.

## 3. Prefetch y ejecución

```powershell
PECmd.exe -d C:\Windows\Prefetch --csv C:\Out --csvf prefetch.csv
```

Se revisan `powershell.exe`, `cmd.exe`, `schtasks.exe`, `certutil.exe` y el nombre del payload. Prefetch da primera/última ejecución, conteo y ficheros abiertos; no prueba por sí solo la intención, pero sitúa la ventana.

## 4. Persistencia

```powershell
Get-ScheduledTask | Where-Object TaskPath -notlike '\Microsoft\*' |
  Select-Object TaskName,TaskPath,State
Get-ChildItem C:\Windows\System32\Tasks -Recurse | Select-String '<C2_HOST>'
```

- Tareas fuera de `\Microsoft\` con un ejecutable en `AppData`/`Temp`.
- Run keys (`HKCU\...\Run`, `HKLM\...\Run`).
- Servicios nuevos (7045) y cambios de `ImagePath`.
- El script `init.ps1` puede crear la tarea con `schtasks /create` o `Register-ScheduledTask`.

## 5. Defender

```powershell
Get-MpPreference | Select-Object ExclusionPath,ExclusionProcess
Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' |
  Where-Object Id -in 1116,1117,5001,5007
```

- Exclusiones añadidas en la ventana del incidente.
- Detecciones 1116/1117 con el nombre del payload.
- 5001/5007 indican que la protección se desactivó o se cambió la configuración.
- Se comprueba si el atacante ejecutó `MpCmdRun.exe` o `Set-MpPreference`.

## 6. Línea temporal

| Hora (UTC) | Evento |
|---|---|
| T0 | `dotnet add package PublishIgnor` |
| T0+1m | `init.ps1` se ejecuta durante la restauración |
| T0+2m | Descarga del payload |
| T0+3m | Creación de la tarea programada |
| T0+4m | Exclusión de Defender |
| T0+5m | Primer beacon |

## Lecciones aprendidas

- Un typosquat en NuGet se ejecuta con los privilegios del usuario que restaura el paquete.
- `init.ps1` es el punto de entrada; el `.nupkg` es la evidencia que hay que conservar.
- En un árbol enorme, la clave es acotar por usuario y por nombre, no recorrer todo.
- Prefetch, tareas y Defender se correlacionan; ninguno basta por separado.
- La cadena de suministro no requiere un exploit: el usuario instala el paquete.

## Mitigaciones y detección

- Usar feeds privados y verificar el propietario del paquete; bloquear nombres similares.
- Revisar `init.ps1`/`install.ps1` antes de restaurar y ejecutar restore sin scripts cuando sea posible.
- Alertar de tareas fuera de `\Microsoft\`, exclusiones de Defender y `schtasks` desde PowerShell.
- Detección: instalación de paquetes con nombre sospechoso, `init.ps1` con descarga, 1116/1117 y 5007.
- Aislar el host, revocar tokens y reconstruir la caché NuGet.

MITRE: T1195.002, T1059.001, T1053.005, T1562.001.

## Referencias

- <https://mwalkowski.com/post/sherlock-nuts>
- <https://attack.mitre.org/techniques/T1195/002/>
- <https://learn.microsoft.com/en-us/nuget/concepts/package-installation>
