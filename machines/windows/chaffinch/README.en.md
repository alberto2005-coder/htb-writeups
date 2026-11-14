---
machine: Chaffinch
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, geoserver, cve-2024-36401, csc, privesc]
---

# Chaffinch — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An exposed GeoServer is vulnerable to CVE-2024-36401: an XPath expression in an OGC parameter executes code without authentication. The shell allows system enumeration and discovery of Windows CSC service credentials or configuration. Abusing the Credential Security Support Provider cache escalates to a more privileged user and completes the box.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p80,443,3389 <IP>
```

- IIS/GeoServer and RDP.
- `chaffinch.htb` with the GeoServer web console.
- Version and WFS endpoint confirm the vulnerable component.

## Enumeration

- GeoServer exposes `/geoserver/web/` and OGC services.
- The version predates 2.22.6/2.23.6/2.24.4/2.25.2.
- The service account and configuration files are reachable after execution.
- Review local tasks, services and credentials.

## Foothold

Send a WFS request with a manipulated property name that GeoTools evaluates as XPath. The expression runs a command and returns a reverse shell as the service user.

```bash
curl -s 'http://<IP>/geoserver/wfs?service=WFS&version=1.0.0&request=GetFeature&typeName=...'
```

## Privilege escalation

The shell allows reading configuration and locating the CSC service. Abuse the Windows credential cache to obtain or modify a privileged user's hash and authenticate as administrator. The exact step depends on the available artifacts; this writeup separates enumeration from abuse.

```powershell
whoami /all
Get-Service | Where-Object Name -like '*CSC*'
```

## Evidence

- GeoServer response with the executed command.
- `whoami` as the service user.
- Local configuration and services enumerated.
- Administrative access after CSC abuse.

## Lessons learned

- GeoServer must be patched and kept off the Internet.
- Property expressions are not inert data.
- Credential cache services are escalation targets.

## Mitigations and detection

- Update GeoServer and restrict `/geoserver`.
- Run the service with a low-privilege account.
- Monitor WFS requests with expressions and anomalous CSC access.
- References: NVD CVE-2024-36401, HTB Chaffinch, Microsoft CSC.

## References

- <https://www.hackthebox.com/machines/Chaffinch>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-36401>
- <https://geoserver.org/vulnerability/2024/09/12/cve-2024-36401.html>
- <https://attack.mitre.org/techniques/T1190/>
