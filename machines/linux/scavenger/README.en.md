---
machine: Scavenger
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, whois, sqli, exim, rootkit, privesc]
---

# Scavenger — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The Whois server on port 43 concatenates the domain into SQL and leaks the hosted domains. One of them leads to a PrestaShop with a webshell, and FTP hands over another customer's credentials. On the host, the loaded `root.ko` module grants root when a password is written to `/dev/ttyR0`; alternatively, Exim 4.89 is vulnerable to CVE-2019-10149 and allows command execution as root over SMTP.

## Recon

```bash
nmap -Pn -sCV -p21,22,25,43,53,80 <IP>
```

- `21` FTP, `22` SSH, `25` Exim, `43` Whois, `53` DNS and `80` HTTP.
- Whois returns a SuperSecHosting banner.
- Hosted domains resolve to internal vhosts.

## Enumeration

Whois is SQL injectable through the domain. Enumerate databases, tables and customers with `UNION SELECT`; one domain is `rentahacker.htb`. A DNS zone transfer reveals the vhosts. `sec03.rentahacker.htb` runs PrestaShop with a vulnerable parameter that allows uploading a webshell.

## Foothold

The webshell is called with `?hidden=id` and runs commands as `ib01c03`. FTP on the same segment holds `ib01c01` credentials, which allow moving to another hosting customer.

```text
http://sec03.rentahacker.htb/shell.php?hidden=id
```

## Lateral movement

The FTP credentials expose another customer's files and the `root.ko` module, along with the password it expects.

## Privilege escalation

`root.ko` creates `/dev/ttyR0`. Writing the module password makes `root_write` compare the buffer with a magic string and, on a match, set every credential to UID/GID 0. The string is built with `snprintf` from two parts, so it must be recovered from the binary or tried in the right variant.

```bash
echo "<string>" > /dev/ttyR0
id
```

The alternative is CVE-2019-10149 in Exim 4.89: an `RCPT TO` address with `${run{...}}` expansion runs commands as root. Use it when SMTP is exposed and the module is unavailable.

## Evidence

- Whois `UNION SELECT` and customer listing.
- Webshell in PrestaShop.
- `root.ko` and `/dev/ttyR0`.
- `id` showing UID 0 after the pushback.

## Lessons learned

- Old services (Whois, FTP) remain attack surface.
- SQLi in a non-web service can enumerate an entire hosting platform.
- Third-party kernel modules are root if their device is writable.
- A misconfigured Exim allows direct RCE over SMTP.

## Mitigation and detection

- Parameterise Whois queries and limit the returned information.
- Update Exim to a fixed version and restrict `RCPT TO`.
- Do not load unsigned kernel modules; audit `/dev/ttyR0`.
- Monitor Exim child processes and writes to new devices.

## References

- [0xdf — Scavenger](https://0xdf.gitlab.io/2020/02/29/htb-scavenger.html)
- [IppSec — Scavenger](https://www.youtube.com/watch?v=rlUTZiqTKgc)
- [Hack The Box — Scavenger](https://app.hackthebox.com/machines/scavenger)
