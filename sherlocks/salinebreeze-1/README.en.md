---
sherlock: SalineBreeze-1
category: Threat Intelligence
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, salt-typhoon, mitre-attack, rootkit, telecom]
---

# SalineBreeze-1 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

A junior analyst is asked to investigate Salt Typhoon and a cyber-espionage campaign against telecommunications networks. The task is to identify the actor, its malware, the vulnerabilities it exploits and the associated MITRE ATT&CK techniques.

## Evidence

- MITRE ATT&CK group profile.
- Vendor reporting on Linux implants and rootkits.
- Government advisories on telecommunications.
- No binaries or PCAP: the investigation is OSINT.

```text
Starting point: the group's MITRE profile and CISA/NSA advisories.
```

## Investigation

### 1. Inventory and triage

Identify the actor's aliases and objective. Salt Typhoon is associated with state espionage and telecommunications infrastructure; documented campaigns include access to routers, switches and management systems.

- Actor linked to China.
- Target: telecommunications networks and critical infrastructure.
- Initial access: valid credentials, edge devices and vulnerabilities in exposed applications.

### 2. Malware and rootkits

Public reporting describes a Linux implant for network devices that captures traffic and wipes logs. Related campaigns use `Demodex`, a kernel-mode rootkit that hides processes and files.

- `JumbledPath` is associated with collection and evidence deletion.
- `Demodex` is installed after access and manipulates the kernel to hide activity.
- Persistence may survive reboots through services or modules.

### 3. MITRE mapping

Map the observed techniques to ATT&CK:

- `T1190` — Exploit Public-Facing Application.
- `T1078` — Valid Accounts.
- `T1014` — Rootkit.
- `T1070.002` — Indicator Removal: Clear Linux or Mac System Logs.
- `T1040` — Network Sniffing.

## Conclusions

- Salt Typhoon combines edge-device access with stealthy implants.
- A rootkit hampers system tools; external telemetry is required.
- Response must include isolation, reimaging and credential rotation.
- Aliases and tools change; TTP mapping is the reusable part.

## Lessons

- APT intelligence must feed detection rules and response plans.
- A rootkit can hide processes, but not all network traffic.
- In telecommunications, the supply chain and edge devices are critical.

## References

- <https://www.hackthebox.com/sherlocks/SalineBreeze-1>
- <https://attack.mitre.org/groups/G1045/>
- <https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-038a>
- <https://attack.mitre.org/techniques/T1014/>
