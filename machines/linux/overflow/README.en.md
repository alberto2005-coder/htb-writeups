---
machine: Overflow
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, padding-oracle, sqli, exiftool, cve-2021-22204, toctou]
---

# Overflow — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A padding oracle in the cookie grants panel access. SQLi leads to the CMS and a crafted image exploits ExifTool CVE-2021-22204 for RCE. Escalation combines an overflow and a TOCTOU in a SUID binary.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443 <IP>
padbuster http://overflow.htb/login "SESSION=<COOKIE>" 16 -cookies "SESSION=<COOKIE>"
# SQLi
sqlmap -u "http://overflow.htb/records.php?id=1" --batch --dump
# ExifTool CVE-2021-22204
exiftool -config exploit.config image.jpg
# TOCTOU
pspy64 -pf -i 1000
while true; do ln -sf /tmp/payload /tmp/target; done
```

## Enumeration

- CBC cookie with a padding oracle and admin panel.
- SQLi in records and a CMS with image upload.
- SUID binary that checks ownership then opens the file.

## Initial access

The padding oracle forges an administrator cookie. SQLi in the records reveals CMS credentials; on upload, a DjVu image with malicious metadata executes code through ExifTool.

## Privilege escalation

A SUID binary checks a file owner and then opens it, leaving a TOCTOU window. Swap the file between the check and the use to execute code as root; the overflow helps control the flow.

## Evidence

- Forged cookie and panel access.
- DjVu metadata image and ExifTool callback.
- File swapped during the TOCTOU window and root shell.

## Lessons learned

- ExifTool processes metadata from exotic formats and can execute code.
- A padding oracle can be the door to a panel.
- TOCTOU turns a check into an illusion.

## Mitigation and detection

- Update ExifTool and disable unnecessary formats.
- Sign cookies and do not leak padding errors.
- Use `openat`/`O_NOFOLLOW` and check the descriptor, not the path.

## References

- [0xdf — Overflow](https://0xdf.gitlab.io/2022/04/09/htb-overflow.html)
- [NVD — CVE-2021-22204](https://nvd.nist.gov/vuln/detail/CVE-2021-22204)
- [Hack The Box — Overflow](https://app.hackthebox.com/machines/overflow)
