---
machine: Eloquia
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, web, angularjs, csti, oauth, sqlite, dpapi, appdomainmanager, privesc]
---

# Eloquia — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

AngularJS CSTI in articles runs directives and bypasses CSP; steal the admin bot's cookie or link its OAuth account. As admin, upload a malicious SQLite extension and load it from SQL Explorer for a `web` shell. Edge saved passwords decrypt with DPAPI and give `olivia.kat`; a writable `.exe.config` allows a malicious AppDomainManager and Administrator.

## Recon

```bash
nmap -Pn -sCV -p80,5985 <IP>
```

- `80` IIS with `eloquia.htb` and `5985` WinRM.
- The Django site has articles, comments and OAuth login against a Google clone (`qooqle.htb`).
- `feroxbuster` enumerates `/admin`, `/accounts` and `/articles`.

## Enumeration

- Article bodies render with AngularJS and allow CSTI.
- CSP blocks inline scripts, but `ng-*` directives evaluate expressions.
- Steal the admin bot's cookie or chain CSRF/OAuth to link the admin account to a controlled one.

## Foothold

As admin, open Django Admin and upload a malicious SQLite `.so` extension. SQL Explorer loads it and runs a function, giving a `web` shell.

```text
SELECT load_extension('/uploads/evil.so');
```

## Lateral movement

The Edge profile has saved passwords. Extract them with `dpapi`/PowerShell and decrypt with the user's key; one works for `olivia.kat` over WinRM.

```powershell
.\dpapi.py credential -file <CRED> -key <KEY>
```

## Privilege escalation

`olivia.kat` can write to `C:\Program Files\Qooqle IPS Software\Failure2Ban - Prototype\Failure2Ban\bin\Debug`. The service restarts periodically and reads `Failure2Ban.exe.config`. Add `<appDomainManagerAssembly>` and `<appDomainManagerType>` pointing to a managed DLL that changes Administrator's password on startup.

```xml
<appDomainManagerAssembly value="admin, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null" />
<appDomainManagerType value="oxdfDomainManager.oxdfManager" />
```

## Evidence

- AngularJS CSTI and CSP bypass.
- Admin cookie/OAuth theft.
- SQLite extension and `web` shell.
- Edge DPAPI and `olivia.kat`.
- `Failure2Ban.exe.config` and Administrator.

## Lessons learned

- Unsanitized AngularJS is client-side expression execution.
- CSP does not protect when dangerous directives are allowed.
- SQLite extensions are native code.
- Edge secrets decrypt with the user's DPAPI.
- A writable `.config` loads a managed DLL into a service.

## Mitigation and detection

- Escape HTML and use `ng-csp`/strict CSP.
- Validate OAuth `state` and `redirect_uri`.
- Do not allow `load_extension` in SQLite.
- Protect browser profiles and credentials.
- Restrict service permissions and sign assemblies.

## References

- [0xdf — Eloquia](https://0xdf.gitlab.io/2026/10/17/htb-eloquia.html)
- [IppSec — Eloquia](https://www.youtube.com/watch?v=aRSUIJXxbDc)
- [Hack The Box — Eloquia](https://app.hackthebox.com/machines/eloquia)
