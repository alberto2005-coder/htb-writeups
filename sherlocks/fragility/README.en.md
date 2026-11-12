---
sherlock: Fragility
category: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, exfiltration, archive, metadata, encoding]
---

# Fragility — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological writeup; no original evidence or literal answers.

## TL;DR

An exfiltrated file containing a hidden message is analysed. Metadata, compression and encoding reveal the sequence and the content.

## Scenario

An organisation detects a suspicious file leaving the network. A copy is provided to determine its contents, how it was hidden and which user prepared it.

## Artefacts

- Compressed file or document.
- Metadata and entry names.
- Strings, hashes and possible steganography.

## Methodology

1. Hash the file and identify its real type with `file`/`binwalk`.
2. List entries and timestamps without extracting.
3. Review metadata and comments.
4. Try compression/encoding layers (base64, gzip, nested ZIP).
5. Document the message and its link to the user.

```bash
file evidence.bin
binwalk evidence.bin
7z l evidence.zip
exiftool evidence.docx
```

## Sample questions

- What is the real file type?
- How many compression layers are there?
- Which user or path appears in metadata?
- What message remains after decoding?
- When was it created/modified?

## Tools

`file`, `binwalk`, `7-Zip`, `ExifTool`, `CyberChef`.

## Evidence and redaction

Hashes, listings and message screenshots are kept with users and paths redacted.

## Lessons learned

- The extension does not determine the real type.
- Nested archives hide simple content.
- Metadata can attribute preparation.
- Documenting layers avoids losing order.

## Detection

- Alert on compression and outbound sensitive data.
- Review double-extension attachments.
- Correlate with network-share access.
- Apply DLP on email and endpoints.

## References

- <https://app.hackthebox.com/sherlocks/Fragility>
- <https://attack.mitre.org/techniques/T1560/001/>
- <https://attack.mitre.org/techniques/T1027/>
