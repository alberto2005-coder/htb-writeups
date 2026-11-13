---
topic: Email header analysis
tags: [forensics, email, spf, dkim, dmarc, phishing, eml]
---

# Email header analysis

**English** | [🇪🇸 Español](email-header-analysis.md)

## Concept

Email headers reconstruct the delivery chain, the real sender and the authentication result. SPF, DKIM and DMARC show whether the domain authorised the message, although a single failure does not prove phishing by itself.

## When it applies

- A suspicious email with an attachment or link.
- Impersonation of a known domain.
- Analysis of a phishing campaign.
- Extracting indicators for blocking.

## Procedure

1. Read the `Received` headers from bottom to top.
2. Compare `From`, `Return-Path`, `Reply-To` and `Message-ID`.
3. Review `Authentication-Results` for SPF, DKIM and DMARC.
4. Decode base64 attachments and nested files.
5. Hash the message and extract domains, IPs and URLs.

```bash
grep -iE '^(Received|From|Return-Path|Reply-To|Message-ID|Authentication-Results):' message.eml
grep -iE 'spf=|dkim=|dmarc=' message.eml
sha256sum message.eml
```

## Variants

- SPF with `softfail` or multiple hops.
- DKIM with a missing selector or broken signature.
- DMARC in `p=none` mode.
- A ZIP attachment containing another archive.

## Limitations

- Headers can be forged.
- An SPF pass does not guarantee legitimacy.
- Forwarders alter the chain.
- Base64 content may be obfuscated or encrypted.

## Mitigation and detection

- Enforce SPF, DKIM and DMARC with a reject policy.
- Block unexpected attachments and macros.
- Alert on mismatches between `From` and `Return-Path`.
- Correlate domains, IPs and hashes with threat intelligence.

## References

- <https://datatracker.ietf.org/doc/html/rfc5321>
- <https://datatracker.ietf.org/doc/html/rfc7208>
- <https://attack.mitre.org/techniques/T1566/001/>
