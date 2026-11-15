---
machine: EvilCUPS
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, cups, ipp, foomatic, printer, command-injection]
---

# EvilCUPS — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

CUPS accepts creating an attacker-controlled printer. Printing a test page makes Foomatic-RIP interpret a malicious attribute and execute commands as `lp`; an old spool job contains the information needed for root.

## Reconnaissance

```bash
nmap -Pn -sCV -p631,80 <IP>
curl -s http://<IP>:631/printers/
# Register a controlled printer
lpadmin -h <IP>:631 -p evil -E -v ipp://<IP>:631/printers/evil
lp -h <IP>:631 -d evil /etc/hostname
# Spool
ls -la /var/spool/cups/
cups-filters /usr/lib/cups/filter/foomatic-rip
```

## Enumeration

- CUPS on `631` with administrative access.
- Foomatic-RIP filters and printer templates.
- Spool with old print jobs.

## Initial access

Register a printer pointing to a controlled server and send a test page. The `cupsFilter` attribute or model name reaches Foomatic-RIP without sanitization, runs the command and returns a shell as `lp`.

## Privilege escalation

The spool keeps an old job with a reconstructable PDF. The document contains credentials or a root path; use it to access root or run a privileged task.

## Evidence

- Printer created through CUPS.
- Test page with callback and shell as `lp`.
- Spool job reconstructed and root access.

## Lessons learned

- A print server is an execution surface.
- Legacy filters interpret attributes as commands.
- The spool retains documents thought to be deleted.

## Mitigation and detection

- Restrict CUPS administration and printer creation.
- Update Foomatic and validate attributes.
- Clean the spool and run CUPS as an unprivileged user.

## References

- [0xdf — EvilCUPS](https://0xdf.gitlab.io/2024/10/02/htb-evilcups.html)
- [CUPS — Documentation](https://openprinting.github.io/cups/doc/)
- [Hack The Box — EvilCUPS](https://app.hackthebox.com/machines/evilcups)
