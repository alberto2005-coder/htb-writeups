---
challenge: Plaintext Tleasure
category: Forensics
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [forensics, pcap, http, credentials, tshark]
type: Forensics
---

# Plaintext Tleasure — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method notes; no real flags.

## TL;DR

A capture of **unencrypted HTTP**. The challenge is the most basic network-analysis exercise: separate useful streams from noise and read them. Credentials and the object of interest sit in request bodies, in clear text, with nothing to decrypt.

## Brief

- Category **Forensics**; the material is a single capture (`capture.pcap` in the challenge package).
- There is no service to attack and no code to review: everything needed is in the file.

## Recon

```bash
capinfos capture.pcap
tshark -r capture.pcap -q -z io,phs
```

`capinfos` gives frame count and duration; the protocol hierarchy says whether TLS is present (in which case nothing is readable) or cleartext HTTP, which is the case here.

## Analysis

1. **Keep HTTP**:

```bash
tshark -r capture.pcap -Y 'http.request' \
  -T fields -e frame.number -e http.request.method -e http.request.uri -e http.host
```

2. **Sort by method**: `POST` first, since that is where credentials and bodies travel.

3. **Follow the right stream**:

```bash
tshark -r capture.pcap -q -z follow,tcp,ascii,<stream>
```

The `POST` carries the form's username/password pair; the server's response carries the object being transferred.

4. **Export what moved**, if there is a file:

```bash
tshark -r capture.pcap --export-objects http,exported/
file exported/*
```

## Root cause

The application sends credentials over **HTTP without TLS**: anyone on the segment — or holding a capture — reads them without breaking anything. There is no cryptographic flaw to exploit; the flaw is the channel design.

## Evidence

- `capture.pcap`.
- In the report: method, URI, host and **redacted** credentials.

## Lessons

- `strings` is no substitute for following the stream: the body is split across TCP segments and `grep` misses it.
- Sorting by method and size saves opening dozens of streams.
- Cleartext HTTP exposes credentials and data: that is why HSTS exists and why internal traffic should be encrypted too.
- If the stream were TLS, only metadata would remain (SNI, sizes, times) and the challenge would have no direct-read solution.

## Mitigations and detection

- TLS site-wide, HSTS and redirect from HTTP; valid certificates on internal services too.
- Never submit credentials through forms served in clear text; `Secure` on session cookies.
- Detection: credentials in `POST` over HTTP, and HTTP traffic to hosts that should speak only HTTPS.

## References

- [Wireshark — Follow TCP Stream](https://www.wireshark.org/docs/wsug_html_chunked/ChAdvFollowStreamSection.html)
- [Hack The Box — Plaintext Tleasure](https://app.hackthebox.com/challenges/Plaintext%20Tleasure)
