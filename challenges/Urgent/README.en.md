---
challenge: Urgent
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, email, phishing, base64, vbscript]
---

# Urgent — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A **phishing** email in full message format. Read the headers, decode the parts (`base64` and *quoted-printable*), resolve links with **URL encoding**, and read the attachment, a **VBScript** that downloads the next stage.

## Evidence

- One email message (`.eml`).

## Method

1. **Header**: real sender, `Return-Path`, sending server and subject.

```bash
grep -iE '^(From|Return-Path|Received|Subject|Date):' mail.eml
```

2. **Body**: usually `multipart/alternative`; the HTML part is base64 or *quoted-printable*.

```bash
python3 -c "import email; m=email.message_from_file(open('mail.eml')); [print(p.get_payload(decode=True).decode('utf-8','replace')) for p in m.walk() if p.get_content_type()=='text/html']"
```

3. **Links**: decode the `%xx` and distrust shorteners and lookalike domains.

```bash
python3 -c "import urllib.parse,sys; print(urllib.parse.unquote(sys.argv[1]))" '<url>'
```

4. **Attachment**: a `.vbs`/`.js` using `WScript.Shell` or `MSXML2.XMLHTTP` means download and execute. Its literals (and variables) give the payload URL and the dropped file name.

5. **IOCs**: sender, subject, payload URL and attachment hash.

## Pitfalls

- **Opening it in a client**: never; analysing the `.eml` as text executes nothing.
- **Multiple body parts**: walk them all, not just the first.
- **Encoded subject**: `=?UTF-8?B?...?=` needs `email.header`.

## Lessons

- An `.eml` is a layered container: headers, encoded parts and attachments.
- URL encoding is obfuscation, not protection; one `unquote` undoes it.
- A VBScript attachment that downloads an executable is the classic phishing chain.
