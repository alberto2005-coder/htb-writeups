---
sherlock: <Name>
domain: <DFIR|SOC|Malware Analysis|Threat Intelligence|Cloud>
difficulty: <Very Easy|Easy|Medium|Hard|Insane>
platform: Hack The Box
state: <Active|Retired>
tags: [dfir, <pcap|memory|evtx|registry|malware>]
---

# <Name> — Hack The Box

**English** | [🇪🇸 Español](sherlock-template.md)

> **State:** <Retired, publishable note | Active, private draft.>
> Investigation notes; no platform answers and no real data.

## Scenario

<Two or three sentences on the incident context and what is asked.>

## Evidence

- <File and what it is.>
- <File and what it is.>

```bash
sha256sum <evidence>        # record hashes before analysing
```

## Investigation

### 1. Inventory and triage

<What gets opened first and why. Concrete commands.>

```bash
<command>
```

### 2. Timeline

<Execution, logons, connections. Which source has reliable time, and in which timezone.>

### 3. Key artifact

<The artifact that cracks the case: exact path, why it matters, what it proves.>

## Findings

- <What happened, in order.>
- <What was taken or changed.>
- <Main IOCs.>

## Lessons

- <What would have caught this earlier.>
- <Concrete mitigation.>
- <Which artifact the organisation is missing.>
