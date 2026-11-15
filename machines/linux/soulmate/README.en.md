---
machine: Soulmate
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, crushftp, erlang, ssh, cve-2025-32433]
---

# Soulmate — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

CrushFTP allows an authentication bypass (CVE-2025-31161) and admin access to upload a webshell. Escalation abuses Erlang/OTP SSH CVE-2025-32433 and an Erlang console running as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p21,22,80,443,8080 <IP>
curl -k https://soulmate.htb:8080/ | grep -i crushftp
# CVE-2025-31161
python3 crushftp_bypass.py -u https://soulmate.htb:8080
# CVE-2025-32433
python3 erlang_ssh_rce.py -t <IP> -p 2222 -c "id"
```

## Enumeration

- Exposed CrushFTP with a vulnerable version.
- Admin access after the bypass and file upload capability.
- Erlang/OTP SSH service on a non-standard port.

## Initial access

The CrushFTP authentication bypass grants administrator access. Upload a JSP or interpreted script and obtain a shell as the service user.

## Privilege escalation

The Erlang/OTP SSH service is vulnerable to CVE-2025-32433: send an authentication message before the handshake completes and execute code in the Erlang console, which runs as root.

## Evidence

- CrushFTP bypass and webshell.
- Access to the Erlang console.
- `id` as root from the console.

## Lessons learned

- File-transfer appliances concentrate privileges.
- An authentication bypass is often enough to upload code.
- A poorly patched Erlang/OTP SSH can execute commands before authentication.

## Mitigation and detection

- Update CrushFTP and Erlang/OTP.
- Restrict administration to loopback and require MFA.
- Monitor uploads and anomalous SSH connections.

## References

- [0xdf — Soulmate](https://0xdf.gitlab.io/2026/02/14/htb-soulmate.html)
- [NVD — CVE-2025-32433](https://nvd.nist.gov/vuln/detail/CVE-2025-32433)
- [Hack The Box — Soulmate](https://app.hackthebox.com/machines/soulmate)
