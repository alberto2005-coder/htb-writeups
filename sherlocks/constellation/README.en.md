---
sherlock: Constellation
domain: Threat Intelligence
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [threat-intelligence, pdf, metadata, exiftool, unfurl, insider]
---

# Constellation — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal platform answers.

## Scenario

An employee receives a document over Discord with instructions to take company data out. The evidence package has no disk or capture: just a PDF and an IOC list. The job is to identify the actor, the infrastructure and when the document was prepared.

## Evidence

```text
constellation/Artifacts/NDA_Instructions.pdf    document sent to the insider
constellation/Artifacts/IOCs.txt                collected URLs and domains
```

```bash
sha256sum Artifacts/*        # record before opening anything
exiftool Artifacts/NDA_Instructions.pdf
```

## Investigation

### 1. Inventory and triage

Two small files, so the PDF sets the order: metadata first, then text, then the URLs in `IOCs.txt`. The PDF carries no JavaScript or attachments; the interest is who generated it and with what tool.

```bash
exiftool -a -G1 -s Artifacts/NDA_Instructions.pdf
```

### 2. Timeline

The metadata gives more than expected: `Producer` and `Creator` point to a tool of the group, `Author` includes the actor's email, and the creation date is impossible (year 2054), a sign of a manipulated clock or a tool writing fake values. The Discord and Google URLs, decomposed with Unfurl, provide real timestamps and the search text the insider typed.

```bash
# paste each URL into https://dfir.blog/unfurl and read timestamp and query
cat Artifacts/IOCs.txt
```

Reconstructed order: recruitment by DM, delivery of the PDF, search for packaging instructions, and upload to an S3 bucket with a taunting name.

### 3. Key artefact

The PDF is the central artefact: its text describes exactly what to compress and where to upload it, and its metadata identifies the author and the tool. Together they turn a generic document into proof of preparation.

## Conclusions

- Actor: a group presenting itself as "AntiCorp", recruiting an insider over Discord.
- Infrastructure: S3 bucket `hahaha-you-lose-forela`, Discord CDN and Google searches used as a covert channel.
- Technique: PDF instructions with careless metadata and URLs carrying timestamps.
- IOCs: PDF author and producer, bucket domain and the URLs in `IOCs.txt`.
- What is missing: no evidence of the exfiltration itself, only of the preparation.

## Lessons

- Document metadata is intelligence: author, tool and impossible dates place the actor and their cadence.
- A CDN or search URL keeps identifiers and times the attacker does not control.
- The bucket name is also an IOC reusable in other campaigns.
- Mitigation: insider-recruitment awareness, DLP on mail and corporate chat, and blocking unapproved storage domains.
- Detection: documents with a non-corporate `Producer`, future dates, and users searching how to compress or upload data.
- What is missing: proxy and CASB log retention to confirm the upload.

MITRE: T1566 (phishing), T1583.001 (acquire infrastructure: domains), T1567.002 (exfiltration to cloud storage), T1078 (valid accounts).
