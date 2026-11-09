---
challenge: Easy Phish
type: OSINT
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [osint, phishing, dns, spf, dmarc]
---

# Easy Phish — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

## Brief

A company sees emails impersonating its domain. Find the attacker's infrastructure: lookalike domain, DNS records and mail server.

## Method

1. **Lookalike domain**: compare the real one with variants (typosquatting, hyphen, different TLD). `dnstwist` generates and resolves candidates:

   ```bash
   dnstwist --registered <company>.com
   ```

2. **DNS**: `dig` the suspect:

   ```bash
   dig +short A <suspect-domain>
   dig +short MX <suspect-domain>
   dig +short TXT <suspect-domain>
   ```

   A `TXT` with `v=spf1` plus one with `v=DMARC1` confirms the attacker set up mail.

3. **Reputation and age**: `whois`, Certificate Transparency (`crt.sh`), VirusTotal and URLScan. A domain days old with a fresh certificate is the signal.

4. **Email headers**: `Received`, `Return-Path`, `Message-ID` and `Authentication-Results`. `Return-Path` usually points to the attacker's domain and `Received` to the real server.

5. **Server IP**: resolve the `A`/`MX` and look the IP up in Shodan/Censys for the mail panel.

## Findings (pattern)

```text
A     <domain> -> <IP>
MX    <domain> -> mail.<domain>
TXT   "v=spf1 a mx ip4:<IP> ~all"
TXT   "v=DMARC1; p=none;"
```

Their own SPF/DMARC plus a dedicated MX indicates live phishing infrastructure.

## Typical errors

- **`dnstwist` finds nothing registered** → the domain does not resolve yet; check `--registered` and CT.
- **The email uses a compromised legitimate domain** → read `Received` in reverse order, not just `From`.
- **Many IPs** → separate `A` from `MX`; mail leaves through the MX.
- **No SPF/DMARC** → the attacker uses a relay; follow the `Return-Path`.

## Lessons

- `From` proves nothing; `Return-Path` + `Received` do.
- Certificate Transparency finds domains before they are indexed.
- A permissive SPF (`~all`) explains why the mail was not marked as spam.

MITRE: T1583.001, T1566.002, T1596.
