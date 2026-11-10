---
title: JEA — running commands on a restricted endpoint and abusing it
tags: [windows, powershell, jea, winrm, privesc]
---

# JEA: restricted endpoints, `& { }` and the PSReadLine history

**English** | [🇪🇸 Español](jea.md)

## 1. What JEA is

*Just Enough Administration* publishes a PowerShell Remoting endpoint (WinRM) that runs as a privileged account but only allows the commands and parameters declared in its *role capability*. The client sees a limited namespace and cannot call arbitrary cmdlets.

From the outside it is just another `PSSessionConfiguration`:

```powershell
Get-PSSessionConfiguration
Get-PSSessionConfiguration -Name '<CONFIG>' | Format-List *
```

## 2. Connect from Linux

`pypsrp` speaks WSMan without Windows:

```python
from pypsrp.client import Client

c = Client('<HOST>', username='<domain>\\<user>', password='<password>', ssl=False)
out, streams, had_errors = c.execute_ps('Get-Command | Select-Object -ExpandProperty Name')
print(out)
```

If the endpoint only accepts Kerberos, `pypsrp` supports `negotiate` with the `ccache` (`KRB5CCNAME`).

## 3. The `& { }` wrapper

The restricted session evaluates the scriptblock with a limited parser: no user functions, no classes, no variables beyond the automatic ones. But `&` with a literal scriptblock is an allowed construct, so grouping several approved statements inside `& { ... }` keeps the parser from rejecting the sequence:

```python
ps = r'''
& {
  $x = Get-ChildItem 'C:\ProgramData\<folder>'
  $x | ForEach-Object { $_.FullName }
}
'''
c.execute_ps(ps)
```

The key point: **only approved cmdlets run**. The wrapper does not bypass the allowlist; it lets you compose several calls and keep the output between statements.

## 4. What is usually allowed and useful

- `Get-ChildItem`, `Get-Content`, `Get-Item` on specific paths.
- `Get-Service`, `Get-Process`, `Get-CimInstance` for allowed classes.
- Custom scripts published in the `RoleCapabilities` (sometimes with unvalidated parameters).

Check the endpoint's `.psrc` (`C:\Program Files\WindowsPowerShell\Modules\...\RoleCapabilities\*.psrc` or the `SessionConfiguration` in the registry) for the real list.

## 5. PSReadLine history

Every user keeps their commands in:

```text
C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt
```

If the endpoint runs as an account with access to that profile (or you can read it with the allowed cmdlets), the history often contains **credentials on the command line**: `net use`, `Invoke-Sqlcmd -Password`, `sshpass`, `runas`. It is one of the fastest ways to go from "I can run four cmdlets" to "I own the endpoint's administrator".

```python
c.execute_ps(r"Get-Content 'C:\Users\<user>\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt'")
```

## 6. Typical errors

- **`The term 'X' is not recognized`** → cmdlet outside the role capability; there is no bypass, look for another allowed one.
- **`Access is denied` with `pypsrp`** → the endpoint requires Kerberos or a specific group; use `-k` with the `ccache`.
- **`Connecting to remote server failed`** → WinRM on 5985/5986 closed or the `ConfigurationName` does not exist.
- **Empty output** → the scriptblock returns no objects; wrap in `Write-Output` if allowed or use `Out-String`.

## 7. Detection and mitigation

- **4104** (script block logging) shows the submitted scriptblock, including the `& { }` wrapper.
- **4688** with `powershell.exe` as a child of `wsmprovhost.exe`.
- JEA transcripts (`TranscriptDirectory`) and WinRM logs.
- Audit role capabilities: least privilege, validated parameters, no `Get-Content` over other users' profiles.
- Restrict who may connect to the endpoint and which account it runs as.

MITRE: T1059.001, T1552.001, T1078.
