---
machine: Aero
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, iis, themebleed, cve-2023-38146, cve-2023-28252]
---

# Aero — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Aero is a Windows 11 host with IIS and a theme repository. A crafted `.msstyles` theme exploits ThemeBleed (CVE-2023-38146) and runs a DLL when previewed. Escalation uses the CLFS kernel flaw associated with Nokoyawa (CVE-2023-28252) to obtain SYSTEM.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,3389 <IP>
```

- IIS on 80 and RDP.
- `aero.htb` with theme sections and upload.
- `feroxbuster` finds the upload panel and `.theme`/`.msstyles` files.

## Enumeration

- The application accepts a theme and previews it.
- The server runs Windows 11 with IIS ARR.
- The build is vulnerable to ThemeBleed and the CLFS flaw.
- A DLL and a `.msstyles` file with the right UNC path must be built.

## Foothold

Create a theme referencing a malicious `.msstyles`; when loaded, Windows resolves a UNC path and downloads a controlled DLL. The DLL runs in the context of the user previewing the theme, returning a shell.

```powershell
# Build the DLL and host it on the UNC resource
# Upload the .theme and request the preview
```

## Privilege escalation

The initial shell is not administrative. Enumerate the CLFS patch level and use the CVE-2023-28252 exploit to corrupt the log file and run code as SYSTEM. The public Nokoyawa variant requires building and running the local exploit.

```powershell
systeminfo
whoami /priv
```

## Evidence

- Theme and `.msstyles` accepted by the application.
- UNC connection and DLL load.
- `whoami` as the IIS user.
- `whoami` as `nt authority\system` after the CLFS exploit.

## Lessons learned

- Themes are native code that Windows loads during preview.
- A UNC path in a theme file can leak credentials or load a DLL.
- CLFS flaws have been used by ransomware; patching is critical.

## Mitigations and detection

- Update Windows and block untrusted theme loading.
- Disable automatic preview and restrict outbound UNC.
- Alert on `.msstyles` creation and processes loading DLLs from network paths.
- References: NVD CVE-2023-38146, CVE-2023-28252, HTB Aero.

## References

- <https://www.hackthebox.com/machines/Aero>
- <https://0xdf.gitlab.io/2023/09/28/htb-aero.html>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-38146>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-28252>
