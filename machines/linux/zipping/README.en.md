---
machine: Zipping
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, zip, symlink, sqli, webshell, reverse-engineering]
---

# Zipping — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The application accepts a ZIP upload and extracts it to a controllable path. A symlink inside the archive reads files outside the upload directory and exposes source code. Review reveals an SQLi that writes a webshell and an LFI that executes it; a binary available with `sudo` is solved through reverse engineering.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH and Apache.
- The site accepts a project ZIP.
- A download section and an admin path exist.

## Enumeration

- The form checks the extension but not the ZIP contents.
- A symlink to `/var/www/html` survives extraction.
- The download returns server files and exposes the code.
- The code builds a SQL query from user input.

## Foothold

Create a ZIP containing a symlink and upload it. Download the result to obtain source and configuration. Use the SQLi to write PHP into a served path; the LFI loads the file and runs commands.

```bash
ln -s /var/www/html target
zip --symlinks payload.zip target
```

## Privilege escalation

A binary available with `sudo` asks for a password and contains the comparison logic. Analyse it with `strings`, `ltrace` and a disassembler; use the recovered password to run it as root.

```bash
sudo -l
strings /path/to/binary
ltrace ./binary
```

## Evidence

- ZIP with a symlink accepted.
- Source code downloaded.
- SQLi and webshell execution.
- Analysed binary and root.

## Lessons

- Extension validation does not validate archive contents.
- Symlinks inside archives can escape the destination.
- SQLi with file writes often becomes RCE.
- Basic reverse engineering solves `sudo` binaries.

## Mitigations and detection

- Extract with options that reject symlinks and absolute paths.
- Use parameterised queries and least-privilege write access.
- Review `sudo` binaries and never embed secrets in comparisons.
- Alert on ZIPs with links and writes to the document root.
- References: OWASP File Upload, CWE-59, HTB Zipping.

## References

- <https://www.hackthebox.com/machines/Zipping>
- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://cwe.mitre.org/data/definitions/59.html>
- <https://attack.mitre.org/techniques/T1505/003/>
