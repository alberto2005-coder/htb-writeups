---
machine: Hackback
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, gophish, log-poisoning, regeorg, winrm, named-pipe, diaghub, privesc]
---

# Hackback — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Port `80` serves a GoPhish instance for phishing campaigns and several brand-impersonating vhosts. One of them leads to `admin.hackback.htb`, a panel with an obfuscated login whose JavaScript check can be bypassed. `webadmin.php` provides a file manager with directory walk, read and write, but PHP and ASPX do not execute. The IIS log is poisoned with a webshell and the manager is used to move across the filesystem; with no RCE, `reGeorg` is uploaded and a SOCKS tunnel reaches WinRM, where credentials from a config file give a shell as `simple`. A misconfigured named pipe allows execution as `hacker`. For SYSTEM, the `UserLogger` service writes a log to a controllable path, allowing a DLL to be placed in `System32`; DiagHub loads it with SYSTEM rights.

## Reconnaissance

```bash
nmap -Pn -sCV -p80,6666,64831 <IP>
```

- `80` Microsoft IIS 10.0.
- `6666` Microsoft HTTPAPI 2.0.
- `64831` TLS with an unidentified service.

```bash
ffuf -u http://<IP> -H "Host: FUZZ.hackback.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <SIZE>
```

Port `80` answers with the GoPhish console, which lists the phishing campaign domains.

## Enumeration

The phishing vhosts (`www.paypal.htb`, `www.facebook.htb`, among others) resolve to the same IP. One panel leads to `admin.hackback.htb`, whose login is protected by a JavaScript check that can be disabled in the browser. The application redirects to a path with a long identifier:

```text
http://admin.hackback.htb/2bb6916122f1da34dcd916421e531578/
```

A `gobuster` run with `.php` finds `webadmin.php`. The panel lists directories, reads files and writes files, but executable extensions are disabled.

## Foothold

With file read and write, the IIS log is poisoned: a request whose `User-Agent` carries PHP code is sent and the log is included from the manager. Since PHP does not execute, the useful path is filesystem reads plus tunnel upload.

`reGeorg` is uploaded (`.aspx` or `.jsp` depending on the server) and a SOCKS client connects:

```bash
python3 reGeorgSocksProxy.py -p 1080 -u http://admin.hackback.htb/<PATH>/tunnel.aspx
proxychains netexec winrm <IP> -u simple -p '<PASSWORD>'
```

The credentials come from a config file read with the manager. WinRM answers through the tunnel and returns a shell as `simple`.

## Lateral movement

`simple`'s shell is constrained by AppLocker and PowerShell language mode. Named pipe enumeration reveals a service pipe that allows command execution in `hacker`'s context. An alternative path is a command injection in `clean.ini`, which reaches the same user.

```powershell
Get-ChildItem \\.\pipe\
```

Execution as `hacker` grants access to more files and the information needed for the next hop.

## Privilege escalation

The `UserLogger` service runs as SYSTEM and writes a log to a path whose ACL allows redirecting it. The log destination is changed to a DLL placed in `C:\Windows\System32`; then DiagHub (Microsoft Diagnostics Hub Standard Collector) is invoked, loading the DLL with SYSTEM rights:

```powershell
reg query HKLM\System\CurrentControlSet\Services\userlogger
# redirect the log and drop the DLL
```

Running the diagnostic service loads the library and returns a SYSTEM shell.

## Evidence

- GoPhish console and phishing vhosts.
- JavaScript login bypass and access to `webadmin.php`.
- Poisoned IIS log and file reads.
- `reGeorg` and SOCKS tunnel to WinRM.
- Shell as `simple` and execution as `hacker` through the named pipe.
- `UserLogger` log redirected and DLL loaded by DiagHub.

## Lessons learned

- An admin panel with file read and write is dangerous even without code execution.
- Log poisoning works for reading and writing, not only for RCE.
- An HTTP tunnel can expose an internal service.
- AppLocker and restricted PowerShell mode do not prevent enumeration and pivoting.
- A service logging to a controllable path can load code as SYSTEM.

## Mitigations and detection

- Remove admin panels from production and require MFA and an IP allowlist.
- Disable file writes in the web manager and validate paths against a base directory.
- Never log unsanitized user headers; keep logs separate from code.
- Restrict tunnel creation and monitor internal SOCKS and WinRM connections.
- Review ACLs on services that write logs and block writes to `System32`.
- Alert on DLL loads from diagnostic services and on `ImagePath` changes.

## References

- [0xdf — Hackback](https://0xdf.gitlab.io/2019/07/06/htb-hackback.html)
- [IppSec — Hackback](https://www.youtube.com/watch?v=B9nozi1PrhY)
- [Hack The Box — Hackback](https://app.hackthebox.com/machines/hackback)
