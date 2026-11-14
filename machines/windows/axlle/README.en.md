---
machine: Axlle
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, xll, phishing, url-file, bloodhound, lolbin]
---

# Axlle — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A domain controller with a corporate website, SMTP, RDP and WinRM. A malicious Excel XLL is sent to `gideon.hamill` and yields a shell; a `.url` file in a shared directory delivers the session to `dallon.matrix`. PowerShell history leaks credentials, BloodHound leads to `baz.humphries`, and the `StandaloneRunner.exe` LOLBIN reaches Administrator.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p25,80,88,389,445,3389,5985 <IP>
bloodhound-python -u <USER> -p <PASS> -d <DOMAIN> -ns <IP> -c All
```

## Enumeration

- AD DS ports, SMTP (25), HTTP (80), RDP and WinRM.
- SMB rejects null and guest access.
- The website lists employees and emails; a shared directory is writable.

## Initial access

Build an Excel XLL carrying a reverse shell and send it over SMTP to `gideon.hamill`; opening it yields a session. On the host, create a `.url` file in a shared path that `dallon.matrix` opens, delivering a second shell. `dallon.matrix`'s PowerShell history contains plaintext credentials.

## Privilege escalation

Use those credentials to collect BloodHound data and identify the path to `baz.humphries`/`jacob.greeny`; change the compromised account password and log in over WinRM. From there, abuse `StandaloneRunner.exe`, a signed LOLBIN, to run a shell with Administrator privileges.

## Evidence

- Email with the XLL and the `gideon.hamill` connection.
- `.url` file and `dallon.matrix` shell.
- BloodHound, WinRM and execution through `StandaloneRunner.exe`.

## Lessons learned

- Office add-ins remain an effective phishing vector.
- `.url` and `.lnk` files in writable shares execute when opened.
- Signed LOLBINs complicate detection and must be audited.

## Mitigation and detection

- Block untrusted XLLs and enforce Mark-of-the-Web.
- Restrict share writes and review `.url`/`.lnk` access.
- Apply WDAC/AppLocker and monitor `StandaloneRunner.exe`.

## References

- [0xdf — Axlle](https://0xdf.gitlab.io/2024/11/16/htb-axlle.html)
- [IppSec — Axlle](https://www.youtube.com/watch?v=cAXptAMDXuY)
- [Hack The Box — Axlle](https://app.hackthebox.com/machines/axlle)
