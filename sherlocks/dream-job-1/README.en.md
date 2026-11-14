---
sherlock: Dream Job-1
category: Threat Intelligence
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, mitre, lazarus, operation-dream-job, iocs]
---

# Dream Job-1 — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal answers or real data.

## Scenario

An intelligence analyst must characterise Operation Dream Job and relate the provided indicators to the Lazarus Group. The goal is to move from a loose IOC to TTPs and an impact assessment.

## Evidence

- `DreamJob1.zip`, protected with the usual password.
- `IOCs.txt` with three lines: two domains/hashes and a wallet address.
- No memory, disk or PCAP.

```bash
unzip DreamJob1.zip
sha256sum IOCs.txt
cat IOCs.txt
```

## Investigation

### 1. Inventory and triage

Record the three indicators and classify them by type: infrastructure, malware and financing. The campaign is identified from the name and scenario context, not from the hash.

### 2. MITRE ATT&CK correlation

```text
Campaign: Operation Dream Job (C0022)
Group: Lazarus Group (G0032)
Tactics: Reconnaissance, Initial Access, Execution, Persistence
```

Review the campaign techniques and separate what the evidence shows from what is inferred about the actor. Do not attribute a technique just because the group used it elsewhere.

### 3. Key artefact

`IOCs.txt` is the only artefact. Query the domains in VirusTotal and MITRE documentation; treat the wallet as payment infrastructure, not C2. Record the query date and confidence.

## Conclusions

- The campaign maps to Lazarus/Operation Dream Job.
- The domains are campaign infrastructure; the hashes identify related samples.
- The wallet provides financial context, not execution.
- Expected impact is espionage and credential theft against defence/technology candidates.

## Lessons

- A single IOC does not prove attribution; campaign context helps.
- Record the source and date of every conclusion.
- Actor intelligence must become concrete detections.

## References

- <https://www.hackthebox.com/sherlocks/Dream%20Job-1>
- <https://attack.mitre.org/campaigns/C0022/>
- <https://attack.mitre.org/groups/G0032/>
