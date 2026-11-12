---
machine: Mailing
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, lfi, hmailserver, cve-2024-21413, monikerlink, ntlm, libreoffice]
---

# Mailing — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An LFI on the site reads hMailServer configuration and allows sending mail as administrator. CVE-2024-21413 (MonikerLink) leaks the administrator's NTLMv2 hash; cracking it grants WinRM access. A LibreOffice macro completes the escalation.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p25,80,110,143,587,5985 <IP>
```

Add `mailing.htb` to hosts. The site has a file viewer and hMailServer handles mail.

## Initial access

The download parameter allows path traversal. Read the hMailServer configuration:

```text
http://mailing.htb/download.php?file=..\..\..\Program Files (x86)\hMailServer\Bin\hMailServer.INI
```

Crack the panel password with `john`/`hashcat`. Log in to hMailServer and create a mailbox.

## Lateral movement

Send an email with a crafted `file://` link (CVE-2024-21413) to a user. When opened, the client connects to a controlled UNC resource and `Responder` captures the NTLMv2 hash. Crack it and log in over WinRM:

```bash
evil-winrm -i <IP> -u <user> -p '<password>'
```

## Escalation to administrator

Review installed applications and user documents. Build a LibreOffice document with a macro that launches a reverse shell; when a privileged user opens it, an administrator shell is obtained.

## Evidence

- Path traversal and redacted configuration.
- MonikerLink email and NTLM capture.
- Redacted cracked hash.
- Macro document and admin shell.

## Lessons learned

- An LFI can expose internal service credentials.
- MonikerLink affects unpatched mail clients.
- NTLMv2 remains useful for lateral movement.
- Document macros remain a vector.

## Mitigation and detection

- Fix the path traversal and validate paths.
- Update Outlook/Windows (CVE-2024-21413).
- Block outbound NTLM and enforce Kerberos.
- Disable macros and apply ASR.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2024-21413>
- <https://www.hackthebox.com/machines/mailing>
- <https://www.hmailserver.com/>
