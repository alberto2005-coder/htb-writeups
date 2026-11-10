---
sherlock: PCAP Analysis
domain: SOC / Network DFIR
difficulty: Very Easy
platform: Hack The Box
state: Retired
evidence: A single capture from one user's host
tools: [Wireshark, tshark, capinfos, xxd]
tags: [dfir, soc, pcap, http, file-upload]
---

# PCAP Analysis — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method notes; no platform answers.

## Scenario

"We have captured this traffic from P13's computer". That is all the brief gives: a capture with thousands of frames where a **plaintext chat** on an unusual port and an **HTTP file upload** coexist.

## Evidence

```text
Pcap_Analysis.zip     (password on the Sherlock page)
Pcap_Analysis.pcapng
```

## Investigation

### 1. Measure before reading

```bash
unzip -P <password> PCAP_Analysis.zip
capinfos Pcap_Analysis.pcapng
tshark -r Pcap_Analysis.pcapng -q -z io,phs
```

`capinfos` gives packet count, duration and sizes; the protocol hierarchy says what is worth filtering. On a capture this size, opening it unfiltered wastes time.

### 2. The chat

The tell is the **non-standard port**: not IRC, not a known protocol, just plaintext over TCP. Filtering that port and rebuilding the payload yields the conversation and both endpoints:

```bash
tshark -r Pcap_Analysis.pcapng -Y 'tcp.port==250 && tcp.len>1' \
  -T fields -e ip.src -e ip.dst -e tcp.payload | xxd -r -p
```

The names in the messages map each speaker to an IP; the chat sender is the same host that later uploads the file.

### 3. The upload

```bash
tshark -r Pcap_Analysis.pcapng -Y 'http.request.method=="POST"' \
  -T fields -e ip.src -e ip.dst -e http.request.uri -e http.content_length
```

The `POST` is `multipart/form-data` to an Apache on another subnet. To read the whole request and its response (which reveals the destination directory):

```bash
tshark -r Pcap_Analysis.pcapng -q -z follow,tcp,ascii,<stream>
```

### 4. The file

`File → Export Objects → HTTP` saves the object; the file is named `file`, about 107 KB, and its content is close to random — already encrypted or compressed. Transfer size comes from the first and last packet of the stream.

## Findings

- Chat sender and upload sender are the same station: one user talking and exfiltrating inside a single capture.
- The conversation is cleartext on a non-standard port, the upload is HTTP without TLS: both channels are readable without breaking anything.
- The uploaded file is opaque (high entropy), so the useful evidence is **who, where and when**, not the content.

## Lessons

- `capinfos` plus the protocol hierarchy turn a large capture into a filter plan.
- A weird port carrying readable text is not "unknown traffic": it is a home-made protocol, and following the stream reads it.
- The server's response confesses more than the request: storage path, Apache version, status code.
- A high-entropy object is not "decrypted" without more data; it is documented as an IOC and correlated.
