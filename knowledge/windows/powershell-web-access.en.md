---
topic: PowerShell Web Access — browser-based remote access
tags: [windows, powershell, pswa, iis, lateral-movement, acute]
---

# PowerShell Web Access — browser-based remote access

[🌐 Español](powershell-web-access.md) | **English**

## Idea

PowerShell Web Access (PSWA) is an IIS gateway exposing a PowerShell console in the browser. It administers hosts without RDP or direct WinRM, which is why it appears on networks that only publish HTTPS. For an attacker it is a full entry point: with valid credentials and a computer name, commands run on the target host, and `Invoke-Command` hops to other machines and restricted endpoints.

## When it applies

- IIS serves `/pswa` or an admin portal asking for user, password and computer.
- Default, reused or leaked credentials exist in documents and metadata.
- PowerShell endpoints (`-ConfigurationName`) are configured to delegate tasks.
- On Acute, the welcome document gave the username format and an initial password, and PSWA logged in to `Acute-PC01`.

## Procedure

1. Discover the portal by directory fuzzing over HTTPS.
2. Obtain credentials plus a list of users and computers.
3. Try the login naming the target computer.
4. Enumerate the session: user, groups, drives, processes and network.
5. Use `Invoke-Command` with the available endpoints to hop to other hosts.
6. Load a post-exploitation tool if the console is limited.

## Commands

```bash
feroxbuster -u https://<IP> -k -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

```text
https://<IP>/pswa
user: <DOMAIN>\<USER>
computer: <HOST>
```

```powershell
whoami /all
Get-ChildItem Env:
Get-Command -Module Microsoft.PowerShell.*
Invoke-Command -ComputerName <HOST> -ConfigurationName <ENDPOINT> -ScriptBlock { whoami; hostname } -Credential $cred
```

```powershell
$pass = ConvertTo-SecureString '<PASSWORD>' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential('<DOMAIN>\<USER>', $pass)
```

## Variants

- If PSWA requires a specific computer, try domain names and management hosts.
- With a limited session, use `powershell.exe -EncodedCommand` to avoid console restrictions.
- If the portal sits behind a proxy, forward requests with `curl` and keep the session cookie.
- Combine it with credentials from documents, email or configuration files.

## Limitations

- Valid credentials and an authorized computer are required.
- MFA or IP restrictions may apply.
- The console may run in restricted mode with no disk access.
- IIS and PowerShell logs record the activity.

## Mitigation

- Disable PSWA unless strictly needed; if used, require MFA and restrict by network.
- Do not publish documents with credentials or internal metadata.
- Apply least privilege to `Invoke-Command` endpoints.
- Rotate initial passwords and forbid reuse.
- Keep administration on a management network.

## Detection

- Requests to `/pswa` from non-administrative networks.
- Successful logins followed by `Invoke-Command` to several hosts.
- `wsmprovhost.exe` and `powershell.exe` process creation on the target.
- Account credentials used from unusual computers.

## References

- [Microsoft — PowerShell Web Access](https://learn.microsoft.com/en-us/powershell/scripting/learn/remoting/pswa)
- [Microsoft — about_Remote_FAQ](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_remote_faq)
- [0xdf — Acute](https://0xdf.gitlab.io/2022/07/16/htb-acute.html)
- [Acute writeup](../../machines/windows/acute/README.en.md)
