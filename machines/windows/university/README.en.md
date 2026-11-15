---
machine: University
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, ad, reportlab, wpad, rbcd, delegation, gmsa]
---

# University — Hack The Box (Windows)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The PDF generator uses ReportLab and is vulnerable to CVE-2023-33733, yielding a shell as `WAO`. A PowerShell script leaks credentials reused on the host and two containers. A malicious URL file executes as a reviewer, WPAD is poisoned to relay NTLM, and a computer with RBCD is created. The container has unconstrained delegation; its tickets lead to a GMSA that can act on the DC.

## Recon

```bash
nmap -Pn -sCV -p53,80,88,135,139,389,445,464,636,3268,3269,5985,9389 <IP>
```

- `53/88/389/445/636` confirm a `university.htb` DC.
- `80/tcp` nginx redirects to the site; `5985/tcp` WinRM is open.
- The site allows professor registration and profile export to PDF.

## Enumeration

- Export uses ReportLab and processes HTML; CVE-2023-33733 executes code during PDF generation.
- A PowerShell script on the host contains `WAO` credentials that also work on the containers.
- `bloodhound` reveals unconstrained delegation and the service GMSA.

## Foothold

Send a CVE-2023-33733 payload in the profile field and obtain a reverse shell as `WAO` when exporting the PDF.

```bash
# register a professor and put the payload in the vulnerable field
# export the profile to PDF and catch the shell
nc -lnvp 443
```

## Lateral movement

With `WAO`, enumerate SMB and the containers. Build a lecture package with a malicious `.url` file that executes as a reviewer. From that session, force WPAD lookups and poison the response from the Linux container, relaying NTLM and creating a computer with RBCD.

## Privilege escalation

The Windows container has unconstrained delegation. Extract Kerberos tickets from memory, identify an account that can read the GMSA, and use `getST.py`/RBCD to act as administrator on the DC.

```bash
Rubeus.exe monitor /interval:5 /nowrap
Rubeus.exe ptt /ticket:<BASE64>
certipy-ad account read -u <USER> -p '<PASSWORD>' -dc-ip <IP> -target dc.university.htb
getST.py -spn cifs/dc.university.htb -impersonate administrator university.htb/<GMSA>$
```

## Evidence

- PDF with CVE-2023-33733 and a `WAO` shell.
- Reused credentials and execution as a reviewer.
- WPAD relay, RBCD, delegation tickets and GMSA.

## Lessons learned

- HTML-to-PDF generation can execute code.
- Script and backup credentials are often reused across hosts.
- WPAD and unconstrained delegation enable deep lateral movement.

## Mitigation and detection

- Update ReportLab and isolate PDF generation.
- Rotate credentials and avoid reuse across containers.
- Disable WPAD, limit delegation and protect GMSAs.

## References

- [0xdf — University](https://0xdf.gitlab.io/2025/08/09/htb-university.html)
- [IppSec — University](https://www.youtube.com/watch?v=q9ms9k02fUM)
- [Hack The Box — University](https://app.hackthebox.com/machines/university)
