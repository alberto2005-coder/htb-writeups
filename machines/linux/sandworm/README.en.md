---
machine: Sandworm
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, ssti, pgp, firejail, cron, rust, cve-2022-31214]
---

# Sandworm — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A PGP verification service is vulnerable to SSTI and runs commands inside Firejail. Cleartext credentials allow SSH; a cron compiles a Rust binary with a writable crate, and Firejail CVE-2022-31214 completes the escalation to root.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80,443 <IP>
```

Add `sandworm.htb` to hosts. The site accepts a signed message and verifies the PGP signature.

## Initial access

The verification field is rendered by a template. Test SSTI:

```text
{{7*7}}
```

Once confirmed, use a payload to run commands. The process runs inside Firejail but can read service files and credentials. Those credentials grant SSH as `atlas`.

## Lateral movement

```bash
pspy64
ls -la /opt
```

A cron compiles and runs a Rust binary. The project uses an external crate in a writable directory; modify it so compilation executes a reverse shell as the cron user.

## Privilege escalation

Firejail is vulnerable to CVE-2022-31214. Run the exploit to create a privileged sandbox and `su` from there:

```bash
./firejail-exploit
```

The resulting shell is root. Read and redact the flag.

## Evidence

- SSTI response and command execution.
- Redacted credentials and SSH.
- `pspy` and modified crate.
- Firejail version and exploit.

## Lessons learned

- SSTI in template engines leads to RCE.
- Firejail does not replace privilege isolation.
- External dependencies of a cron are executable code.
- CVE-2022-31214 affects old Firejail versions.

## Mitigation and detection

- Escape input and never render templates with user data.
- Update Firejail.
- Pin dependencies and make them read-only.
- Monitor builds and cron child processes.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2022-31214>
- <https://www.hackthebox.com/machines/sandworm>
- <https://github.com/DominicBreuker/pspy>
