---
sherlock: UFO-1
category: Threat Intelligence
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, mitre, sandworm, apt44, ics]
---

# UFO-1 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal answers or real data.

## Scenario

An analyst in the ICS sector must study Sandworm Team (APT44) through MITRE ATT&CK. There are no artefacts: the evidence is public documentation and the ability to map campaigns to techniques.

## Evidence

- No ZIP or artefacts.
- Work from MITRE ATT&CK, CISA and public reporting.
- Answers rest on group G0034 and its campaigns.

```text
Group: Sandworm Team (G0034), also BlackEnergy/APT44
Key campaign: 2016 Ukraine Electric Power Attack (C0015)
```

## Investigation

### 1. Inventory and triage

Identify the group and list documented campaigns. Separate initial-access, physical-impact and evasion techniques.

### 2. Timeline

Order the milestones:
- 2009: documented origins.
- 2015/2016: Ukrainian electric grid campaign.
- 2017: NotPetya.
- 2022: Industroyer2 and infrastructure attacks.

### 3. Key artefact

The artefact is the ATT&CK group page and its Navigator layer. Record technique IDs and check whether each has a cited source.

```bash
# Navigator: load G0034 and export the layer
```

## Conclusions

- Sandworm is a state actor focused on critical infrastructure.
- Its campaigns combine remote access, modular malware and destructive impact.
- ATT&CK mapping prioritises ICS/IT telemetry.
- Attribution relies on official sources, not a single IOC.

## Lessons

- Threat intelligence can be done without malware.
- ICS techniques require physical context.
- Citing sources prevents over-attribution.

## References

- <https://www.hackthebox.com/sherlocks/UFO-1>
- <https://attack.mitre.org/groups/G0034/>
- <https://attack.mitre.org/campaigns/C0015/>
