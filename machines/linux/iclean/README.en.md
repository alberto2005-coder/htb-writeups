---
machine: IClean
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, xss, ssti, flask, qpdf, privesc]
---

# IClean — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The cleaning site generates quotes and QR codes. XSS in the quote field reaches the admin bot and steals its cookie, whose `role` is the MD5 of `admin`. The QR generator is vulnerable to Jinja SSTI and yields a shell as `www-data`. The database holds `consuela`'s SHA-256, which cracks; that account can run `qpdf` under sudo and attach root's private key to a PDF.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH and `80` Flask.
- Quote form, QR generator and admin panel.
- The site is called Capiclean.

## Enumeration

Review the routes and available code. The quote field is reflected unescaped and there is a button for an administrator to review it. The QR generator passes text into a Jinja template. On the host, `consuela` has a SHA-256 hash in the database.

## Foothold

Submit a quote with `<script>` or an `img onerror` so the bot opens it and exfiltrates its cookie. The stolen cookie already contains the administrator role (`role` = MD5 of `admin`), so it can be reused to open `/dashboard`. The panel generates QR codes; the parameter reaches `render_template_string`, and `{{7*7}}` confirms SSTI.

```text
{{ cycler.__init__.__globals__.os.popen('id').read() }}
```

## Lateral movement

The SSTI runs commands as `www-data`. The code and database reveal `consuela`'s hash; `hashcat -m 1400` cracks it and the password works over SSH.

## Privilege escalation

`consuela` can run `/usr/bin/qpdf` as root with her password. `qpdf` can create an empty PDF and attach any file root can read. Attach `/root/.ssh/id_rsa`, extract it from the PDF and use it to log in as root.

```bash
sudo qpdf --empty --add-attachment /root/.ssh/id_rsa -- out.pdf
qpdf --show-attachment=id_rsa out.pdf
```

## Evidence

- Quote with JavaScript and a request from the bot.
- Cookie with an administrator `role`.
- `{{7*7}}` evaluated in the QR.
- PDF with root's private key attached.

## Lessons learned

- XSS in an admin view can become account takeover.
- A role derived from a known hash adds no security.
- Jinja templates must never receive user text.
- Legitimate tools with sudo can read privileged files.

## Mitigation and detection

- Escape output and use `HttpOnly`/`SameSite` cookies.
- Do not derive roles from guessable values; sign and validate server-side.
- Use fixed templates with strict Jinja context.
- Restrict `qpdf` under sudo and audit PDFs created with attachments.

## References

- [0xdf — IClean](https://0xdf.gitlab.io/2024/08/03/htb-iclean.html)
- [IppSec — IClean](https://www.youtube.com/watch?v=DYp9TFnZH-g)
- [Hack The Box — IClean](https://app.hackthebox.com/machines/iclean)
