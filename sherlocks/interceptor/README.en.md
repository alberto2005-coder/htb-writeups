---
sherlock: Interceptor
domain: SOC / Network
difficulty: Easy
platform: Hack The Box
evidence: Traffic capture of an SSLoad infection
tools: [Wireshark, tshark, CyberChef, Python]
---

# Interceptor — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

A SOC spots suspicious outbound activity. The capture holds the full infection chain of an **SSLoad**-style loader: an **MSI** downloaded over **WebDAV**, execution, and **RC4-encrypted C2** traffic.

## Evidence

- One PCAP with web, WebDAV and outbound connections.

## Method

1. **Initial download**: look for `.msi` requests and WebDAV methods (`PROPFIND`, `OPTIONS`, `GET` with `Depth`).

```bash
tshark -r interceptor.pcap -Y 'http.request' -T fields -e http.host -e http.request.method -e http.request.uri
```

2. **Execution chain**: the MSI runs `msiexec` and drops a binary or script; Sysmon/EDR would show the parent, here it is inferred from traffic and downloaded content.

3. **C2**: identify host and pattern (POST with a binary body, custom `User-Agent`, regular intervals).

4. **Decrypt**: the body is **RC4**; the key usually lives in the binary or is derived from the `User-Agent`/URI. Try CyberChef with payload candidates.

```bash
tshark -r interceptor.pcap -Y 'http.request.method=="POST"' -T fields -e http.host -e tcp.payload | head
```

5. **Extract the next stage**: the decrypted JSON reveals commands, paths and new URLs. Record IOCs.

## What it teaches

- WebDAV is a delivery favourite because many networks allow the methods and filtering does not inspect them.
- An MSI, signed or not, run by the user is code execution without exploiting anything.
- RC4 C2 has a clear signature: fixed-length, high-entropy bodies.

## Pitfalls

- **TLS traffic**: if the download is encrypted, only SNI, sizes and timestamps remain.
- **The RC4 key**: without the loader sample, test candidates taken from the traffic itself.
- **Update noise**: separate by `User-Agent` and destination before reading bodies.
