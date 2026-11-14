---
machine: AdmirerToo
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, adminer, ssrf, opentsdb, fail2ban, opencats]
---

# AdmirerToo — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An image gallery running Adminer 4.7.8 and an internal OpenTSDB. An Adminer SSRF (CVE-2021-21311) reaches OpenTSDB, whose command injection (CVE-2020-35476) yields a shell as `opentsdb`; credentials in `servers.php` allow SSH as `jennifer`. Locally, OpenCats 0.9.5.2 (CVE-2021-25294) writes `whois.conf`, and fail2ban runs the `whois` query, leading to root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://<DOMAIN> -H "Host: FUZZ.<DOMAIN>"
```

## Enumeration

- `db.admirer-gallery.htb` exposes Adminer 4.7.8 with an already authenticated session.
- Ports 4242 (OpenTSDB) and 8080 (OpenCats) only listen on localhost.
- Adminer's `servers.php` stores database and `jennifer` credentials.

## Initial access

The Elasticsearch login module makes Adminer request an attacker server, which redirects it to `http://127.0.0.1:4242`. The SSRF reaches OpenTSDB and its command injection provides a shell as `opentsdb`. Reading `servers.php` reveals `jennifer`'s password, reused over SSH.

## Privilege escalation

As `jennifer`, OpenCats is found on port 8080. The PHP deserialization flaw in CVE-2021-25294 allows file writes; `phpggc` builds a chain that creates `/usr/local/etc/whois.conf`. fail2ban runs `whois` against the attacker IP, and the file turns that query into a command executed as root.

## Evidence

- Adminer response containing OpenTSDB output.
- Shell as `opentsdb` followed by SSH access as `jennifer`.
- Modified `whois.conf` and fail2ban execution as root.

## Lessons learned

- An SSRF with redirects can reach loopback-only services.
- Administration panels leak credentials for other services.
- fail2ban runs system binaries with attacker-influenced configuration.

## Mitigation and detection

- Restrict Adminer and require strong authentication.
- Do not run OpenTSDB unauthenticated on localhost.
- Control writes to `/usr/local/etc` and audit fail2ban actions.

## References

- [0xdf — AdmirerToo](https://0xdf.gitlab.io/2022/05/28/htb-admirertoo.html)
- [IppSec — AdmirerToo](https://www.youtube.com/watch?v=446sWtb5bc4)
- [Hack The Box — AdmirerToo](https://app.hackthebox.com/machines/admirertoo)
