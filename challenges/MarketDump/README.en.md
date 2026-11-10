---
challenge: MarketDump
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, http, base58, exfiltration]
---

# MarketDump — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

In the PCAP, an attacker who pivoted through the web walks off with the customer database over **clear-text HTTP**. Every card number starts the same except one; that outlier is not base64 but **base58**, and it decodes to the flag.

## Brief

`MarketDump.zip` → `MarketDump.pcapng`. No binary, no server: the traffic and the dump inside it are the evidence.

## Recon

```bash
capinfos MarketDump.pcapng
tshark -r MarketDump.pcapng -Y 'http.response' -T fields -e frame.number -e ip.src -e content_type | head
```

`Statistics → Protocol Hierarchy` shows HTTP plus database traffic: the attacker came in through the web and left with a dump.

## The flaw

`File → Export Objects → HTTP` lists one large object, `costumers.sql`, formatted as `IssuingNetwork,CardNumber`:

```bash
strings costumers.sql | head -20
strings costumers.sql | awk -F, '{print $2}' | awk '{print substr($0,1,1)}' | sort | uniq -c
```

Almost every number shares its first digit; **one** does not. That value has base58's length and alphabet (no `0`, `O`, `I`, `l`), not base64's.

## Exploitation

```bash
echo -n 'NVCijF7n6peM7a7yLYPZrPgHmWUHi97LCAzXxSEUraKme' | base58 -d
```

Or CyberChef's *From Base58* recipe. The output is the flag.

```text
HTB{<flag>}
```

There is no need to import the `.sql` into MySQL: it is plain text and `strings`/`grep` read it.

## Evidence

- Trimmed output; no flags or real card data.
- Real values live in `private/`.

## Lessons

- **base64 first, but not only**: when the standard alphabet fails, try base58/base62 before giving up.
- **The outlier is the signal**: in a synthetic dump, the odd value is the interesting one.
- **`Export Objects`** recovers the whole file without rebuilding streams by hand.
- **`.sql` is text**: no database needed to read it.

- Clear-text HTTP turns any dump into a public download.
- Encoding is not encryption: identifying the alphabet solves the challenge.
- Mitigation: HTTPS end to end, no exceptions for internal panels, and card data encrypted at rest.

## Difficulty note

HTB lists it as **Easy**; one community index records it as **Medium**. It stays Easy here and the discrepancy is noted.
