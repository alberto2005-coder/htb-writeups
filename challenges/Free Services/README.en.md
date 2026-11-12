---
challenge: Free Services
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, email, phishing, eml, attachment, malware]
---

# Free Services — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A malicious email in `.eml` format is analysed. Headers reveal the real sender, infrastructure and client; the body contains an encoded link or attachment. Extracting and decoding the attachment yields the payload and the flag.

## Brief and surface

- Forensics, Easy, retired.
- An `.eml` or a ZIP containing the email is provided.
- The goal is to identify the attack and extract the indicator.

```bash
file suspicious.eml
head -40 suspicious.eml
```

## Recon

Review `Received`, `From`, `Reply-To`, `Return-Path` and `Message-ID` headers. Extract URLs and attachments:

```bash
munpack suspicious.eml
exiftool suspicious.eml
```

## Analysis

The body may be base64 or quoted-printable. Decode it and review links carefully (without visiting them). If there is an attachment, hash it and inspect its real type:

```bash
base64 -d attachment.b64 > attachment.bin
file attachment.bin
sha256sum attachment.bin
```

If the attachment is an archive or a macro document, analyse it in an isolated VM. The flag is often in the subject, attachment name or decoded content.

## The bug

The email relies on sender appearance and an attachment/link the user may open. MIME encoding hides the real content and headers can be forged.

## Local reproduction

1. Parse the `.eml`.
2. Extract and decode MIME parts.
3. Analyse URLs and attachments.
4. Locate and redact the flag.

## Evidence

- Headers with domains and addresses redacted.
- Attachment hash.
- Decoded content with the flag redacted.

## Lessons learned

- `Received` headers help trace origin.
- MIME base64/quoted-printable hides content.
- Attachments must be analysed in isolation.
- A “free” offer is a classic lure.

## Mitigation and detection

- Email filtering and attachment analysis.
- SPF, DKIM and DMARC.
- Block macros and executables.
- Phishing awareness training.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/free-services/>
- <https://www.rfc-editor.org/rfc/rfc5322>
- <https://attack.mitre.org/techniques/T1566/001/>
