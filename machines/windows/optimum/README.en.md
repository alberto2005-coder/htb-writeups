---
machine: Optimum
os: Windows
difficulty: Easy
platform: Hack The Box
category: Web / Windows
state: Retired
tags: [rejetto, hfs, cve-2014-6287, ms16-032, windows]
---

# Optimum — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Only one port: **80** running `HttpFileServer 2.3` (Rejetto HFS). The `%00` search macro (CVE-2014-6287) executes commands as `kostas`; reaching **SYSTEM** uses **MS16-032** (Secondary Logon handle), or any UAC bypass of that era.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
80/tcp open  http   HttpFileServer httpd 2.3
```

The page identifies itself as `HFS 2.3` in the header and title.

## Access

**CVE-2014-6287** — the search parameter (`search=%00{.exec|...}`) ends up in a `find` call without sanitising:

```text
GET /?search=%00{.exec|cmd.exe /c powershell -nop -w hidden -c "..." .}
```

MSF module: `exploit/windows/http/rejetto_hfs_exec` → session as `kostas`.

## Escalation

`kostas` is a normal user: check patches and privileges.

```text
systeminfo
whoami /priv
```

**MS16-032** (CVE-2016-0099) escalates from a process holding multiple handles in the Secondary Logon service; the public exploit compiles through PowerShell and spawns a `NT AUTHORITY\SYSTEM` shell. Contemporaries: Watson, or `JuicyPotato` when `SeImpersonate` is present.

## Pitfalls

- **32 vs 64-bit payloads**: the box is from 2016; an x64 binary will not start on an x86 OS.
- **Blind execution**: no output in the response, so a reverse shell is easier.
- **Defender**: may delete the exploit binary; use `C:\Windows\Temp` and compile in memory.

## Lessons

- An end-user file server on port 80 is web surface, with RCE CVEs.
- On old Windows, escalation is usually **missing patches**, not misconfiguration.
- `systeminfo` + `whoami /priv` pick the path in a minute.
