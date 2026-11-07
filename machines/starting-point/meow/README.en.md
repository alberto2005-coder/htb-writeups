---
machine: Meow
os: Linux
difficulty: Very Easy
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/394
category: Starting Point
state: Retired
pwned: 2026-11-05
tags: [telnet, ftp, misconfiguration]
---

# Meow — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired · Starting Point · Linux · Very Easy

## TL;DR

The box exposes **Telnet (23/tcp)** and allows logging in as `root` **with no password**. A root shell and the flag are obtained in under a minute.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

Relevant result:

```text
PORT   STATE SERVICE VERSION
23/tcp open  telnet  Linux telnetd
```

- Only one port is open: **23/tcp (Telnet)**.
- No HTTP, SSH or SMB. Telnet is the only attack surface.
- `nmap -sV` identifies a Linux `telnetd` (typical of lab images).

## Enumeration

Telnet is a plain-text protocol. Before brute forcing anything, check whether it accepts **default or empty credentials**:

```bash
telnet <TARGET_IP>
```

The server prompts for a login:

```text
login: root
Password:
```

Leaving the password empty (just `Enter`) is accepted.

## Foothold

```bash
telnet <TARGET_IP>
# login: root
# Password: <Enter>

id
cat /root/flag.txt
```

```text
uid=0(root) gid=0(root) groups=0(root)
<FLAG>
```

There is no exploitation here: it is a **misconfiguration**. Telnet is enabled and the `root` account has no password, so anyone with network connectivity gets full control.

## Lessons learned

- **Telnet should be treated as obsolete:** it sends credentials and the entire session in clear text.
- Trying empty or default credentials is a valid, fast step in labs (and still works on poorly configured real networks).
- Enumerating **all** ports matters: without `-p-` you might miss port 23.
- The box shows that the smallest attack surface can be the most critical one.

## Mitigations and detection

**How to fix it:**

- Disable Telnet and use **SSH** with key-based authentication.
- Forbid empty passwords (`pam`/`/etc/shadow`).
- Block direct remote `root` login (`PermitRootLogin no`).
- Segment and filter the management network.

**How it would be detected:**

- Alerts on inbound connections to port 23.
- Audit rules for `root` logins from remote IPs.
- Configuration review: `telnetd` installed/running without justification.

## References

- [OWASP — Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [CIS Benchmarks — Linux](https://www.cisecurity.org/benchmark/distribution_independent_linux)
- MITRE ATT&CK: [T1078 Valid Accounts](https://attack.mitre.org/techniques/T1078/), [T1021 Remote Services](https://attack.mitre.org/techniques/T1021/)
