---
machine: Reel2
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, owa, password-spray, responder, jea, powershell, sticky-notes]
---

# Reel2 — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Wallstant social network on 8080 allows names to be collected; they feed password spraying against OWA. After login, a malicious link captures a NetNTLM hash with Responder and it is cracked. The account receives a restricted JEA session, escaped with functions and the call operator; StickyNotes leaks `jea_test_account` credentials and its `Check-File` function reads the root flag.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,443,8080,5985 <IP>
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt -u http://<IP>:8080/FUZZ
```

## Enumeration

- IIS on 80/443, Wallstant on 8080 and WinRM on 5985.
- Wallstant allows account registration and user listing.
- OWA on 443 is the spray target.

## Initial access

Collect names from the social network and test a common password against OWA with SprayingToolkit. With valid credentials, log in and send a link to an attacker-controlled UNC resource; Responder captures the NetNTLMv2 hash, which is cracked. The credentials allow WinRM, but the session is restricted by JEA.

## Privilege escalation

The JEA session blocks cmdlets but allows function definitions and `&{ ... }`; that bypass launches a FullLanguage PowerShell. `Documents` holds the `.psrc`/`.pssc` files for `jea_test_account` and StickyNotes stores its password. Connect with `-ConfigurationName jea_test_account` and use `Check-File C:\ProgramData\..\Users\Administrator\Desktop\root.txt`.

## Evidence

- Valid spray and OWA session.
- Captured and cracked NetNTLMv2 hash.
- JEA bypass and flag read with `Check-File`.

## Lessons learned

- User enumeration feeds password spraying.
- Responder remains effective when outbound SMB is allowed.
- A poorly configured JEA role can be escaped with functions and call operators.

## Mitigation and detection

- Enforce MFA and lockout after failed OWA attempts.
- Block outbound SMB and require signing.
- Audit JEA roles and avoid functions that read arbitrary paths.

## References

- [0xdf — Reel2](https://0xdf.gitlab.io/2021/03/13/htb-reel2.html)
- [IppSec — Reel2](https://www.youtube.com/watch?v=Ro2vXt_WFDQ)
- [Hack The Box — Reel2](https://app.hackthebox.com/machines/reel2)
