---
sherlock: PhishNet
category: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [soc, phishing, email-headers, spf, base64, zip]
---

# PhishNet — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A user reports a suspicious email. The analyst must confirm its origin, check sender-domain authentication, analyse the attachment and extract indicators to block the campaign.

## Evidence

- Original `.eml` message with full headers.
- Attachment base64-encoded inside the message.
- Public DNS records for the sender domain.
- Hashes calculated over the message and attachment.

```bash
sha256sum <EVIDENCE>.eml
```

## Investigation

### 1. Headers and delivery chain

`Received` headers are read bottom-up to rebuild the route. `Return-Path`, `From`, `Reply-To` and `Message-ID` are compared; discrepancies often reveal spoofing.

```bash
grep -iE '^(Received|From|Return-Path|Reply-To|Message-ID|Authentication-Results):' message.eml
```

SPF is checked against the source IP, DKIM against the selector and DMARC against the aligned domain. An SPF failure alone does not prove phishing, but together with domain mismatch it is strong evidence.

### 2. Attachment

The attachment is base64-decoded and identified by magic bytes, not extension. SHA-256 is calculated and the ZIP is inspected without extraction.

```bash
base64 -d attachment.b64 > attachment.bin
file attachment.bin
7z l attachment.bin
sha256sum attachment.bin
```

### 3. Content and persistence

Inside the ZIP, names, timestamps and any executable, LNK or macro-enabled document are reviewed. Double extensions and extraction paths are common indicators. The flow maps to MITRE T1566.001.

## Conclusions

- Real sender domain and IP.
- SPF, DKIM and DMARC results.
- Attachment nature and hashes, redacted.
- Recommended action: block sender, domain and network IOCs.

## Lessons

- The visible extension does not determine the file type.
- SPF, DKIM and DMARC are interpreted together, not separately.
- A seemingly harmless ZIP may contain an LNK or executable.

## References

- <https://www.hackthebox.com/sherlocks/PhishNet>
- <https://attack.mitre.org/techniques/T1566/001/>
- <https://datatracker.ietf.org/doc/html/rfc7208>
- <https://learn.microsoft.com/en-us/microsoft-365/security/office-365-security/email-authentication-dmarc-configure>
