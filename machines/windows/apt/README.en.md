---
machine: APT
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, ad, ipv6, ntlm, kerberos, dcsync]
---

# APT — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Only RPC and HTTP respond over IPv4, but RPC leaks an IPv6 address that exposes all DC ports. An anonymous SMB backup contains `ntds.dit` and the SYSTEM registry; after cracking the ZIP, 2,000 hashes are dumped. Hash reuse gives registry access, then `henry.vinson_adm` and WinRM. With NTLMv1 enabled, coercion and relay provide DCSync rights.

## Recon

```bash
nmap -Pn -sCV -p80,135 <IP>
```

- `80/tcp` IIS 10 serving a hosting site and `135/tcp` MSRPC; the remaining ports appear filtered.
- RPC answers `IOXIDResolver` and returns an IPv6 address for the DC.
- Scanning that IPv6 address reveals `53`, `88`, `389`, `445`, `5985` and the rest of the AD services.

## Enumeration

- The `backup` share allows anonymous access and contains `backup.zip` with `Active Directory/ntds.dit` and `registry/SYSTEM`.
- `zip2john` and `hashcat -m 17220` recover the ZIP password.
- `secretsdump.py -system ... -ntds ... LOCAL` extracts about 2,000 hashes; `kerbrute` confirms `henry.vinson` as a valid user.

## Foothold

`henry.vinson`'s hash does not work directly, so every hash from the dump is tested with `pyKerbrute` until the matching one is found. That hash queries the remote registry and reads `henry.vinson_adm` credentials from `HKU\SOFTWARE\GiganticHostingManagementSystem`; that account has WinRM access.

```bash
secretsdump.py -system registry/SYSTEM -ntds 'Active Directory/ntds.dit' LOCAL > ad_dump
cat ad_dump | grep ':::' | cut -d: -f3-4 > hashes
python3 pyKerbrute.py -domain htb.local -users henry.vinson -passwords hashes -dc-ip <IP>
reg.py -hashes :<HASH> htb.local/henry.vinson@htb.local query -keyName 'HKU\SOFTWARE\GiganticHostingManagementSystem'
evil-winrm -i <IP> -u henry.vinson_adm -p '<PASSWORD>'
```

## Lateral movement

`henry.vinson_adm`'s PowerShell history reveals that `lmcompatibilitylevel=2` was set, enabling NTLMv1. RoguePotato forces a privileged account to authenticate, and a custom RPC server with `ntlmrelayx` relays it to LDAP, where DCSync rights are granted.

## Privilege escalation

With the relay complete, run `secretsdump.py` against the DC to dump every domain hash, including `administrator`, and gain full access.

```bash
ntlmrelayx.py -t ldap://<DC> -smb2support --escalate-user henry.vinson_adm
secretsdump.py -just-dc htb.local/administrator@<DC>
```

## Evidence

- DC IPv6 address obtained through RPC.
- `backup.zip` downloaded and hashes dumped.
- WinRM access as `henry.vinson_adm` and completed DCSync.

## Lessons learned

- IPv6 services can expose ports that IPv4 filters.
- An SMB-accessible AD backup is equivalent to compromising every account.
- NTLMv1 and authentication coercion remain a viable chain.

## Mitigation and detection

- Restrict IPv6 and RPC to the administrative network.
- Encrypt and restrict AD backups; never expose `ntds.dit` over anonymous SMB.
- Disable NTLMv1, enforce signing and monitor LDAP relays.

## References

- [0xdf — APT](https://0xdf.gitlab.io/2021/04/10/htb-apt.html)
- [IppSec — APT](https://www.youtube.com/watch?v=eRnqtXwCZVs)
- [Hack The Box — APT](https://app.hackthebox.com/machines/apt)
