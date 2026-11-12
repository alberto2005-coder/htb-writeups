---
topic: WSUS abuse for remote execution
tags: [windows, wsus, active-directory, privesc, sharpwsus]
---

# WSUS abuse for remote execution

**English** | [🇪🇸 Español](wsus-abuse.md)

## Concept

Windows Server Update Services (WSUS) distributes updates to domain hosts. A WSUS administrator can publish a local update and approve it for a machine; the client downloads and runs the associated binary. If an attacker controls an account with publishing rights, they can use a Microsoft-signed binary such as `PsExec.exe` to execute code as SYSTEM on the target.

## When it applies

- The domain uses WSUS and clients point at it (`WUServer` in the registry).
- The compromised account belongs to `WSUS Administrators` or can publish updates.
- The attacker can reach port 8530/8531 and the client will check in.

## Requirements and conditions

1. Authenticated access to the WSUS server.
2. Ability to create and approve an update for the target.
3. A Microsoft-signed payload (Sysinternals) or a chain that uses one.
4. The client accepts the update and runs the installer.

## Procedure

Enumerate the server from the compromised host:

```powershell
Get-ItemProperty HKLM:\software\policies\microsoft\windows\WindowsUpdate
.\SharpWSUS.exe locate
.\SharpWSUS.exe inspect
```

Create the update with a signed binary and arguments:

```powershell
.\SharpWSUS.exe create /payload:'C:\ProgramData\PsExec.exe' \
  /args:'-accepteula -s -d C:\ProgramData\payload.exe' \
  /title:'Critical Update'
```

Approve it for the host or group:

```powershell
.\SharpWSUS.exe approve /updateid:<ID> /computername:<FQDN> /groupname:'<GROUP>'
.\SharpWSUS.exe check /updateid:<ID> /computername:<FQDN>
```

The client downloads the binary, runs it as SYSTEM and returns the shell or completes the action.

## Variants

- **WSUSpendu**: publishes and approves a signed binary; useful without the SharpWSUS console.
- **PsExec as payload**: no custom signature needed because PsExec is already signed.
- **`WSUSTemp`/`WsusContent`**: publishing shares; access depends on configuration.
- **Console attack**: if the attacker can modify the WSUS database, updates can be injected without the UI.

## Limitations

- WSUS only runs Microsoft-signed binaries; a custom EXE will not execute.
- The client must check in; this can take time or require `gpupdate`/a reboot.
- The update must be approved for the right machine.
- WSUS over HTTPS with strict validation can block local publishing.

## Mitigation

- Separate `WSUS Administrators` from user accounts and require MFA for the console.
- Publish only signed updates from a verified source.
- Use HTTPS, restrict 8530/8531 and segment the WSUS server.
- Audit groups with publishing rights and Windows Update GPOs.

## Detection

- Event 7045 (new service) and `PsExec` execution from `C:\ProgramData`.
- Child processes of `wuauclt.exe`/`TrustedInstaller.exe` launching unexpected binaries.
- New local updates in the WSUS database and approvals outside the change window.
- Connections to 8530 from hosts that are not admin servers.

MITRE ATT&CK: T1072 (Software Deployment Tools), T1068 (Exploitation for Privilege Escalation), T1543.003 (Windows Service).

## References

- <https://learn.microsoft.com/en-us/windows-server/administration/windows-server-update-services/get-started/windows-server-update-services>
- <https://github.com/Th3M3/SharpWSUS>
- <https://attack.mitre.org/techniques/T1072/>
