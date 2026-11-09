---
sherlock: PCAP Analysis
domain: DFIR / Network
difficulty: Very Easy
platform: Hack The Box
evidence: A single traffic capture from a user host
tools: [Wireshark, tshark, CyberChef]
---

# PCAP Analysis — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

A capture taken from a user's host holds a **plaintext chat** and an **HTTP file upload**. With roughly 25,000 frames, the task is to separate the conversation from the noise and pull the file out.

## Evidence

- A single `Pcap_Analysis.pcapng`.

## Method

1. **Cut the noise**: `Statistics → Protocol Hierarchy` and `Conversations`.

```bash
tshark -r Pcap_Analysis.pcapng -q -z io,phs
```

2. **The chat**: filter on the cleartext messaging protocol and follow the stream.

```bash
tshark -r Pcap_Analysis.pcapng -Y 'http' -T fields -e _ws.col.Info | head
```

3. **The upload**: find the `POST` carrying `multipart/form-data` and export the object.

```bash
tshark -r Pcap_Analysis.pcapng -Y 'http.request.method=="POST"' -T fields -e http.request.uri
```

`File → Export Objects → HTTP` saves the file; its size appears in the server's response.

4. **The file**: `file` finds no signature (it reports data), so inspect the content and the multipart header to learn what was uploaded.

## What it teaches

- In a large PCAP the first step is always reduction: protocols, conversations, then content.
- Clear-text chat plus an HTTP upload give a name, an intent and proof of exfiltration.
- `Export Objects` avoids rebuilding multipart by hand.

## Pitfalls

- **Field name**: in multipart, `name=` is the form field and `filename=` the real file name.
- **Background noise**: update traffic and DNS dominate the frames; filter before reading.
- **Encryption**: if the upload rides TLS, only metadata remains (SNI, sizes, times).
