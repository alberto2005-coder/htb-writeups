---
machine: Precious
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, ruby, pdfkit, ssrf, yaml-deserialization, sudo]
---

# Precious — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The application converts a URL to PDF with `pdfkit` and can be pointed at internal resources. File reads and the vulnerable `pdfkit` version lead to command execution as the service user. A Ruby script run with `sudo` and attacker-controlled YAML provide root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH and HTTP.
- The site advertises web-page-to-PDF conversion.
- `robots.txt` and errors reveal Ruby.

## Enumeration

- The form accepts a URL and returns a PDF.
- `pdfkit` accepts schemes such as `file://` and internal paths.
- The response exposes generator metadata and its version.
- An internal application and a root-run maintenance script are present.

## Foothold

Start with a harmless `/etc/passwd` read through `file://`. Then abuse `pdfkit`/`wkhtmltopdf` option injection to run a command and obtain a reverse shell as the service user.

```bash
curl -s 'http://precious.htb/' --data-urlencode 'url=file:///etc/passwd'
```

The vulnerable version lets the attacker inject command-line parameters; use a controlled callback to confirm execution before stabilising the shell.

## Privilege escalation

The user can run an update script with `sudo`. The Ruby script loads YAML from a writable path; replace it with a Ruby object that executes a command during deserialisation.

```bash
sudo -l
find / -writable -type f 2>/dev/null | head
```

Validate the change locally, run the script with `sudo`, and verify the result without publishing the flag.

## Evidence

- PDF generated from an internal URL.
- Read of a system file.
- `id` as the service user.
- `sudo` execution of the Ruby script and root.

## Lessons

- A URL-to-PDF converter is an SSRF and file-read surface.
- PDF metadata identifies the exact library version.
- YAML deserialisation in Ruby can execute objects.
- A root-run maintenance script deserves a full review.

## Mitigations and detection

- Restrict allowed schemes, hosts and ports in the converter.
- Update `pdfkit` and `wkhtmltopdf`; never concatenate options.
- Use `YAML.safe_load` and least privilege for `sudo` scripts.
- Alert on requests to `127.0.0.1`, `file://` and maintenance-script changes.
- References: CVE-2022-25765, OWASP SSRF, HTB Precious.

## References

- <https://www.hackthebox.com/machines/Precious>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-25765>
- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://attack.mitre.org/techniques/T1190/>
