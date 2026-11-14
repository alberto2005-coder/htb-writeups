---
sherlock: Dream Job-2
category: Threat Intelligence
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, lazarus, dratzarus, torisma, malware]
---

# Dream Job-2 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal answers or real data.

## Scenario

A follow-up to Dream Job-1. Analyse the custom malware and tools Lazarus used in the campaign, map them to MITRE ATT&CK and extract reusable indicators.

## Evidence

- A nested ZIP with a sample and a safety note.
- The inner ZIP needs another password given in the note.
- Do not run the sample: static and intelligence analysis only.

```bash
7z l DreamJob2.zip
sha256sum *
strings -a sample | head
```

## Investigation

### 1. Inventory and triage

Identify inner files, hash them and separate the sample from documentation. The note warns about malware: work in an isolated VM.

### 2. Tooling and family

```text
DRATzarus: RAT associated with Lazarus
Torisma: loader/backdoor with lz4 packing and VEST-32 encryption
```

Compare names, strings and functions with MITRE documentation and public reporting. Note which traits are visible in the sample and which come from literature.

### 3. Key artefact

The note and malware name drive the ATT&CK navigation. Look for execution, persistence, encryption and C2 techniques, and discard any not supported by the evidence.

## Conclusions

- The campaign uses custom malware alongside public tools.
- DRATzarus and Torisma provide remote access and evasion.
- IOCs should be correlated with Dream Job-1 infrastructure.
- The impact remains targeted espionage.

## Lessons

- Static analysis avoids running dangerous samples.
- Malware intelligence is validated across sources.
- Naming a family is not evidence of its capabilities.

## References

- <https://www.hackthebox.com/sherlocks/Dream%20Job-2>
- <https://attack.mitre.org/campaigns/C0022/>
- <https://attack.mitre.org/groups/G0032/>
