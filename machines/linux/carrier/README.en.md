---
machine: Carrier
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, snmp, router, bgp, ftp, privesc]
---

# Carrier — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SNMP exposes the `r1` router configuration and administrative credentials. The diagnostics panel runs commands as root, giving control of `r1`. From there, announce a BGP route to the FTP server, capture traffic and recover credentials that allow host access and root.

## Recon

```bash
nmap -Pn -sU -sCV -p161 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` a transport management application.
- SNMP answers with a valid community and leaks processes and configuration.
- `gobuster` finds `/diagnostics` and the admin panel.

## Enumeration

- `snmpwalk` reveals the `r1` panel username and password.
- `/diagnostics` runs `ping` and `traceroute`; the parameter is not sanitized.
- The internal network uses BGP and the host has an FTP server with credentials.

## Foothold

Inject a command into diagnostics and get a root shell on router `r1`. From there, change the BGP configuration to announce a more specific route to the FTP server.

```bash
curl -s -b 'PHPSESSID=<SESSION>' 'http://<IP>/diagnostics.php' --data-urlencode 'target=127.0.0.1; id'
```

## Lateral movement

`r1` announces the route and the host's FTP traffic crosses the router. `tcpdump` captures the cleartext credentials; use them to SSH into the Linux server.

```bash
tcpdump -i any -nn -A 'tcp port 21'
```

## Privilege escalation

The captured account has root privileges or allows reusing the `root` password; `su` yields the flag.

```bash
ssh <USER>@<IP>
su -
```

## Evidence

- `snmpwalk` with router credentials.
- Injection in `/diagnostics` and a root shell on `r1`.
- Announced BGP route and FTP capture.
- Reused credentials and root on the host.

## Lessons learned

- SNMP can leak a router's full configuration.
- Diagnostics passing input to `system` is root execution.
- Unauthenticated BGP allows traffic diversion and credential capture.

## Mitigation and detection

- Use SNMPv3 and ACLs; do not expose the community.
- Validate diagnostics parameters and run unprivileged.
- Sign BGP (RPKI/BGPsec) and encrypt FTP with TLS.

## References

- [0xdf — Carrier](https://0xdf.gitlab.io/2019/03/16/htb-carrier.html)
- [IppSec — Carrier](https://www.youtube.com/watch?v=2ZxRA8BgmnA)
- [Hack The Box — Carrier](https://app.hackthebox.com/machines/carrier)
