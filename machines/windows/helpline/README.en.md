---
machine: Helpline
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, manageengine, servicedesk, xxe, lfi, winrm, efs, privesc]
---

# Helpline — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

ManageEngine ServiceDesk Plus accepts the guest account and leaks an Excel password audit. XXE (CVE-2017-9362) reads `it_logins.txt` and gives `alice` over WinRM; credentials in logs and files chain to `leo` and an administrator. Separately, LFI CVE-2017-11511 and the SDP panel reach SYSTEM; sensitive files use EFS and are decrypted with Mimikatz.

## Recon

```bash
nmap -Pn -sCV -p135,445,5985,8080 <IP>
```

- `8080` ManageEngine ServiceDesk Plus.
- `5985` WinRM, `445` SMB and `135` RPC.
- The host is Windows and the panel uses local authentication.

## Enumeration

The default `guest:guest` account works. The solutions section has a password audit Excel with users and a reference to `C:\Temp\Password Audit\it_logins.txt`.

## Foothold

Exploit XXE in the SDP API (CVE-2017-9362) to read `it_logins.txt` and get `alice` credentials. Use them over WinRM.

```bash
python3 mesep_xxe.py <IP> "C:\temp\Password Audit\it_logins.txt"
```

## Lateral movement

From `alice`, review event logs and accessible files; `zachary` and then `tolu` credentials appear. `tolu` reaches the `E:` drive, where a PowerShell script can be injected to get `leo`. `leo`'s desktop has administrator credentials in XML.

## Privilege escalation

The other path uses LFI CVE-2017-11511 to download panel files and reach the SDP database. As SDP administrator, change the PostgreSQL password and abuse a trigger to run as SYSTEM. Important files use EFS; Mimikatz/`crypto` decrypt the keys and read the flags.

## Evidence

- `guest:guest` and password audit.
- XXE CVE-2017-9362 and `alice`.
- Logs/credentials to `tolu` and `leo`.
- LFI CVE-2017-11511 and SDP panel.
- PostgreSQL trigger, SYSTEM and EFS.

## Lessons learned

- Guest accounts on old panels remain useful.
- XXE can read internal files and credentials.
- Event logs and IT backups accumulate secrets.
- EFS does not protect once SYSTEM and keys are obtained.
- A database trigger can execute code.

## Mitigation and detection

- Disable guest accounts and change defaults.
- Update ServiceDesk Plus and disable XXE.
- Restrict WinRM and audit log access.
- Protect EFS with separate accounts and rotate secrets.
- Review triggers and PostgreSQL permissions.

## References

- [0xdf — Helpline](https://0xdf.gitlab.io/2019/08/17/htb-helpline.html)
- [IppSec — Helpline](https://www.youtube.com/watch?v=Vs3oSDlzxwA)
- [Hack The Box — Helpline](https://app.hackthebox.com/machines/helpline)
