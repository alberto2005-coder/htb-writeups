---
sherlock: ElectricBreeze-1
category: Threat Intelligence
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, mitre-attack, volt-typhoon, apt, osint]
---

# ElectricBreeze-1 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A security team wants to assess exposure to Volt Typhoon. As a junior threat intelligence analyst, you are asked to research the group, map its tactics and techniques to MITRE ATT&CK, and explain which credential and persistence techniques matter to an organization.

## Evidence

- Public MITRE ATT&CK group profile.
- CISA and allied advisories on Volt Typhoon.
- Vendor reporting on edge-device exploitation.
- No malware or capture is provided: the evidence is OSINT.

```text
Primary source: https://attack.mitre.org/groups/G1017/
```

## Investigation

### 1. Inventory and triage

Start with the MITRE profile, which summarizes the actor, aliases and observed techniques. Record activity dates, targeted sectors and the techniques with the highest impact for the organization.

- Tracked as Volt Typhoon / Vanguard Panda / BRONZE SILENCE.
- Active since at least 2021.
- Primary target: critical infrastructure and telecommunications networks.
- Initial access tied to edge devices and valid credentials.

### 2. Credentials and Active Directory

MITRE lists two `T1003` sub-techniques for the group: LSASS Memory (`T1003.001`) and NTDS (`T1003.003`). The latter targets Active Directory's `ntds.dit` database.

Decrypting `ntds.dit` requires the `SYSTEM` hive, which holds the boot key. Without it, the file cannot be decrypted practically.

```text
T1003.003 → NTDS → Active Directory → SYSTEM hive
```

### 3. Edge exploitation and persistence

Public reporting describes exploitation of a Versa Director zero-day in 2024 (CVE-2024-39717) and the use of valid credentials to move through the network. Persistence relies on local accounts, services and system tasks rather than loud malware.

- `T1190` — Exploit Public-Facing Application.
- `T1078` — Valid Accounts.
- `T1053` — Scheduled Task/Job.
- `T1562.001` — Impair Defenses: Disable or Modify Tools.

## Conclusions

- Volt Typhoon prioritizes stealth and valid credentials.
- NTDS extraction and service-account abuse are direct risks.
- Defense must cover edge devices, segmentation, MFA and privileged-account monitoring.
- Infrastructure IOCs change quickly; TTPs are more stable.

## Lessons

- Threat intelligence must become detections and controls, not just an IOC list.
- MITRE ATT&CK helps compare coverage but does not replace local evidence.
- A nation-state actor can operate for months with built-in tools.

## References

- <https://www.hackthebox.com/sherlocks/ElectricBreeze-1>
- <https://attack.mitre.org/groups/G1017/>
- <https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-038a>
- <https://nvd.nist.gov/vuln/detail/CVE-2024-39717>
