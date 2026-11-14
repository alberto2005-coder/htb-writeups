---
topic: Printers and PJL
tags: [hardware, printer, pjl, pret, filesystem, base64]
---

# Printers and PJL

**English** | [🇪🇸 Español](printer-pjl.md)

## Concept

PJL (Printer Job Language) is a control language used by HP-compatible printers. It can query status, change settings and access an internal filesystem. If the print port is exposed without authentication, jobs, fonts and configurations can be listed and downloaded.

## When it applies

- Network printers with port 9100 open.
- Admin panels with default credentials.
- Jobs retained under `saveDevice` or `spool`.
- Hardware challenges with a print service.

## Procedure

1. Identify the service and banner.
2. Connect with PRET in PJL mode.
3. List the filesystem and navigate.
4. Download the file of interest.
5. Decode if the content is base64.

```bash
nmap -Pn -sV -p 9100 <IP>
python2.7 pret.py <IP>:9100 pjl
```

## Variants

- `FSUPLOAD`/`FSDOWNLOAD` to read or write files.
- `FSDIRLIST` to enumerate directories.
- Jobs under `saveDevice/SavedJobs/InProgress`.
- PDFs or documents encoded in base64.
- PostScript or FTP exposed on the same device.

## Limitations

- PJL may be disabled or filtered.
- Some models require authentication for the filesystem.
- PRET depends on Python 2.7.
- Modern firmware limits dangerous commands.

## Mitigation and detection

- Disable PJL and unused ports.
- Segment printers on a VLAN and restrict by IP.
- Change credentials and delete retained jobs.
- Alert on PJL commands, `saveDevice` downloads and anomalous port 9100 access.

## References

- <https://github.com/RUB-NDS/PRET>
- <https://hacking-printers.net/wiki/index.php/Printer_Security_Testing_Cheat_Sheet>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1005/>
