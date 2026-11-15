---
machine: RustyKey
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, timeroasting, rbcd, 7zip]
---

# RustyKey — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Assume-breach scenario with a low-privilege AD account. ACL and group analysis allows writing an SPN and performing Timeroasting; hijacking the 7-Zip shell extension provides lateral movement and RBCD against the DC leads to administrator.

## Reconnaissance

```bash
nmap -Pn -sCV -p53,88,389,445,5985 <IP>
nxc smb <DC> -u <USER> -p "<PASS>" --shares
bloodhound-python -u <USER> -p "<PASS>" -d rustykey.htb -c All
timeroast.py -d rustykey.htb -u <USER> -p "<PASS>"
# 7-Zip and RBCD
Rubeus.exe asktgt /user:<USER> /rc4:<HASH>
Rubeus.exe s4u /impersonateuser:Administrator /msdsspn:cifs/<DC> /ptt
```

## Enumeration

- Initial credentials for an unprivileged domain account.
- ACLs and groups that allow modifying accounts and computers.
- 7-Zip installed and a modifiable Windows shell context.

## Initial access

With the initial account, enumerate AD and identify write permissions on objects. Add an SPN to a computer account and use Timeroasting to obtain crackable material offline.

## Privilege escalation

Hijack the 7-Zip shell extension in a more privileged user's profile and execute in their context. From there, configure RBCD against the DC and request a service ticket to administer the domain.

## Evidence

- ACL enumeration and writable SPN.
- Cracked Timeroasting hashes.
- Configured RBCD and administrator ticket.

## Lessons learned

- Assume breach requires enumerating permissions, not just services.
- Computer-account SPNs are sensitive material.
- Desktop shell extensions are persistence and lateral movement.

## Mitigation and detection

- Audit ACLs and remove unnecessary writes on computers.
- Monitor SPN changes and Timeroasting.
- Restrict shell extensions and enforce LAPS/Protected Users.

## References

- [0xdf — RustyKey](https://0xdf.gitlab.io/2025/11/08/htb-rustykey.html)
- [Timeroasting — Secura](https://www.secura.com/blog/timeroasting)
- [Hack The Box — RustyKey](https://app.hackthebox.com/machines/rustykey)
