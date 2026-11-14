---
machine: Anubis
os: Windows
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [windows, asp, jamovi, adcs, pkinit, active-directory]
---

# Anubis — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

ASP injection in a public application provides a shell in a Windows container. From there an internal application can send requests to a controlled Responder and leak domain credentials. SMB access allows a malicious Jamovi file to be uploaded, yielding a host shell, and a writable ADCS template with PKINIT leads to Administrator.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,443,445,3389 <IP>
```

- IIS/ASP, SMB, RDP and internal services.
- The public application has a vulnerable form.
- The domain and controllers are enumerated from the container.

## Enumeration

- ASP injection runs commands in the container.
- Enumerate networks, users and internal resources.
- An internal application accepts URLs and is vulnerable to SSRF.
- Responder captures domain credentials.
- The SMB resource contains or accepts Jamovi files.

## Foothold

Exploit ASP injection for a container shell. Pivot to the internal application and use SSRF to make it authenticate to Responder; the hash/credentials allow mounting the SMB share and uploading a Jamovi file with execution.

```bash
curl -s 'http://<IP>/page.asp?cmd=whoami'
responder -I <IFACE> -wv
```

## Privilege escalation

The certificate template allows a smart-card-logon certificate request. Add the EKU attribute, request the certificate and configure PKINIT to obtain an Administrator TGT.

```powershell
Certify.exe find /vulnerable
Certipy-ad req -u <USER> -p <PASS> -ca <CA> -template <TEMPLATE>
```

## Evidence

- ASP execution in the container.
- Credentials captured by Responder.
- Jamovi file executed on the host.
- Issued certificate and Administrator TGT.

## Lessons

- A compromised container can be the pivot point.
- SSRF plus Responder turns a request into credentials.
- Documents from analysis applications can execute code.
- A misconfigured ADCS template can yield Domain Admin.

## Mitigations and detection

- Validate ASP input and isolate containers.
- Block unnecessary SMB/HTTP egress and sign SMB.
- Restrict ADCS templates and review EKU/permissions.
- Alert on certificate requests and anomalous PKINIT authentication.
- References: ADCS ESC, Certipy, HTB Anubis.

## References

- <https://www.hackthebox.com/machines/Anubis>
- <https://posts.specterops.io/certified-pre-owned-d95910965cd2>
- <https://github.com/ly4k/Certipy>
- <https://attack.mitre.org/techniques/T1649/>
