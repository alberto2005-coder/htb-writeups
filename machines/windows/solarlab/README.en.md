---
machine: SolarLab
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, smb, reportlab, cve-2023-33733, openfire, runascs, privesc]
---

# SolarLab — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An SMB share exposes documents and an Excel file with usernames and passwords. The ReportHub application generates PDFs with ReportLab 3.6.12 and passes form fields into the template. CVE-2023-33733 escapes the sandbox and gives a shell as `blake`. The code and `users.db` reveal `openfire` credentials; RunasCs gets that account, and OpenFire's encryption key decrypts the Administrator password.

## Recon

```bash
nmap -Pn -sCV -p80,135,139,445,6791,7680 <IP>
```

- `80` and `6791` redirect to ReportHub; `135` RPC, `139`/`445` SMB and `7680` an unknown service.
- RDP (3389) and WinRM (5985/5986) are not exposed.
- The `Documents` share is reachable as `guest`.
- ReportHub creates leave, training and travel requests and exports a PDF.

## Enumeration

`Documents` holds an Excel file with usernames and passwords. RID brute force and `ffuf` enumerate usernames; spraying the sheet's passwords finds `blake`'s, which logs in to ReportHub on `6791`. The application code lives in `C:\Users\blake\Documents\app` and uses ReportLab to build the PDF.

## Foothold

The application passes form fields such as `phone` or `destination` into PDF generation. ReportLab 3.6.12 is vulnerable to CVE-2023-33733: a `<font color="...">` tag with an expression built from `getattr` and `__globals__` runs code during rendering. The server returns a 500, but the command executes.

```text
<font color="[[getattr(pow,W('__globals__'))['os'].system('ping <IP>')for W in [o('W',(str,),{...})]] for o in [type(type(1))]]">e</font>
```

## Lateral movement

As `blake`, read `app.py`, `routes.py` and `instance/users.db`. The SQLite database stores plaintext passwords; one belongs to `openfire`. `RunasCs.exe` starts a session with those credentials and returns a shell as `openfire`.

## Privilege escalation

OpenFire is installed in `C:\Program Files\Openfire`. Its configuration stores the Administrator password encrypted with Blowfish/CBC and keeps the key in `openfire.xml`. A script that reproduces the decryption recovers the Administrator password; `psexec.py` over SMB gives SYSTEM.

```bash
psexec.py solarlab.htb/administrator:'<password>'@solarlab.htb powershell
```

The alternative is CVE-2023-32315 in OpenFire 4.7.4: `%u002e%u002e` traversal creates an administrator and uploads a plugin with RCE.

## Evidence

- Shared Excel with usernames and passwords.
- ReportHub request with the `<font color>` tag.
- `users.db` with users and passwords.
- Decrypted Administrator password and `psexec.py`.

## Lessons learned

- SMB-shared documents contain application secrets.
- ReportLab evaluates expressions in a font colour.
- Plaintext passwords in SQLite widen lateral movement.
- An encryption key stored next to the ciphertext defeats the protection.

## Mitigation and detection

- Upgrade ReportLab to 3.6.13 or later and never evaluate user HTML.
- Restrict the SMB share and protect documents with strong passwords.
- Hash application passwords and separate the encryption key.
- Audit user and plugin creation in OpenFire.

## References

- [0xdf — SolarLab](https://0xdf.gitlab.io/2024/09/21/htb-solarlab.html)
- [IppSec — SolarLab](https://www.youtube.com/watch?v=BGp_Y3tbLP0)
- [Hack The Box — SolarLab](https://app.hackthebox.com/machines/solarlab)
