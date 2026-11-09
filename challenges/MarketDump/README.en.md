---
challenge: MarketDump
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, http, base58, exfiltration]
---

# MarketDump — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

In the PCAP, an attacker who pivoted through the web app walks off with the customer database over cleartext HTTP. Every card number starts the same way except one: that is the interesting one, and it is encoded in **base58**.

## Evidence

- `MarketDump.zip` → `MarketDump.pcapng`.

## Method

1. **Traffic overview**: `Statistics → Protocol Hierarchy`. Besides HTTP there is database traffic, confirming the web pivot.

2. **Extract the object**: `File → Export Objects → HTTP` lists `costumers.sql`. Save it and inspect:

```bash
strings costumers.sql | head -20
```

The format is `IssuingNetwork,CardNumber`. Nearly all numbers start with `3`; one does not.

3. **Decode the outlier**: the odd string is not base64 (that fails), it is **base58**:

```bash
echo -n '<string>' | base58 -d
```

CyberChef's *From Base58* recipe works too.

4. **Context**: follow the server response's TCP stream (`Follow → TCP Stream`) to see the whole download and who requested it.

## Pitfalls

- **base64 first**: it looks like base64 and is not; try base58 and base62 before discarding it.
- **Many streams**: filter on `http.response` and by size — the database dump is the largest.
- **.sql file**: no need to import it into MySQL; `strings` reads it fine.

## Lessons

- Exporting HTTP objects is the fastest way to recover cleartext exfiltration.
- Encoding is not encryption: identifying the alphabet (base58 avoids `0OIl`) solves it.
- Mitigation: HTTPS on every hop, with no exceptions for internal panels.
