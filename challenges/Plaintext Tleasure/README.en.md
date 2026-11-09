---
challenge: Plaintext Tleasure
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, http, credentials, strings]
---

# Plaintext Tleasure — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A capture with **unencrypted HTTP**: the streams show administrator credentials and the flag itself in clear text. It is the most basic network-forensics drill and builds the *follow the stream* reflex.

## Evidence

- `capture.pcap`.

## Method

1. **Shortcut** (valid here, not always):

```bash
strings capture.pcap | grep -i 'HTB{'
```

2. **Proper route**: protocol hierarchy and conversations.

```bash
tshark -r capture.pcap -q -z io,phs
tshark -r capture.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

3. **Follow the stream**: find the login `POST` and use `Follow → HTTP Stream`; username, password and the server response are all there.

4. **Document**: which credentials were sent, to which host, and when (`frame.time`).

## Pitfalls

- **`strings` misleads**: if the capture compresses segments or the text is split, `grep` misses it; the stream does not.
- **Many streams**: sort by size and method (`POST` first).
- **HTTP/2**: binary framing defeats `strings`; use the dissector.

## Lessons

- Cleartext HTTP exposes credentials and data: the reason HSTS exists and internal traffic should be encrypted too.
- `Follow → HTTP Stream` is the basic tool of network forensics.
- `strings` is a shortcut; understanding the flow is what belongs in a report.
