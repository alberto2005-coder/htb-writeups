---
sherlock: "AoTR 2: Operation Winter Blackout"
category: Threat Intelligence
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [threat-intelligence, forum, phishing, infrastructure, osint]
---

# AoTR 2: Operation Winter Blackout — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

After a logistics company compromise, investigators access a private forum used by the group. It contains conversations about an operation named Winter Blackout. Identify the members, infrastructure and target.

## Evidence

- Forum export and credentials from the previous investigation.
- Profiles, messages, images and infrastructure addresses.
- Forum access logs and file metadata.

```bash
sha256sum forum-export.zip
unzip -l forum-export.zip
```

## Investigation

### 1. Inventory and triage

Catalog users, roles, threads and attachments. Aliases and signatures group messages. Record dates and normalize time zones.

```bash
grep -RInE 'Curator|Bellringer|SnowFox|Driver_BUD|Ledger' forum/
```

### 2. Timeline

Messages show planning: reconnaissance, target selection, infrastructure purchase and OPSEC rules. Sort by date and correlate with mentioned domains and accounts.

### 3. Key artifact

Images and links reveal geolocation, providers and real names. One alias leaks a name in casual conversation; another posts a screenshot with metadata. Together they attribute roles and anticipate the next step.

## Conclusions

- The group has at least five members with distinct roles.
- The operation targets a specific logistics company.
- Infrastructure uses reused domains and accounts.
- Poor forum OPSEC enables partial attribution.

## Lessons

- A private forum is intelligence, not just malware.
- Correlate aliases with timestamps, style and metadata.
- Images can leak location and names.
- Threat intelligence must cite sources and separate inference from fact.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://medium.com/@andrginting/hackthebox-aotr-2-operation-winter-black-bfb559d9f945>
- <https://attack.mitre.org/resources/centers/intel/>
