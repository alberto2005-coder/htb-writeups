---
sherlock: Takedown
domain: DFIR / Network
difficulty: Easy
platform: Hack The Box
evidence: Network capture of an SMB and PowerShell intrusion
tools: [Wireshark, tshark, CyberChef]
---

# Takedown — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

The team spots an anomalous traffic pattern: an intrusion that begins with a **VBS** file dropped on a share and continues with a PowerShell download and beaconing to a C2. It is all in the capture.

## Evidence

- One PCAP with SMB2, HTTP and outbound connections.

## Method

1. **SMB session**: SMB2 negotiation, NTLM authentication and a `Tree Connect` to a share.

```bash
tshark -r takedown.pcap -Y 'smb2' -T fields -e frame.number -e _ws.col.Info | head -40
```

2. **File created**: a `Create Request` drops a `.vbs` on the share. That name is the initial-access IOC.

3. **Execution**: the VBS launches PowerShell, which downloads a script over HTTP; follow the stream for the URL and its content.

```bash
tshark -r takedown.pcap -Y 'http.request' -T fields -e http.host -e http.request.uri
```

4. **Stolen authentication**: a `NTLMSSP_AUTH` means the hash was reused; type and account identify the lateral move.

5. **C2**: periodic POSTs to an external IP. Interval and size profiling gives the beacon shape.

## What it teaches

- A reachable share is a delivery point: the attacker writes, the victim executes.
- The SMB → VBS → PowerShell → HTTP sequence is a full intrusion chain inside one PCAP.
- NTLM on a flat network enables pass-the-hash without ever touching the password.

## Pitfalls

- **SMB2 compression or encryption**: without the session key only metadata remains.
- **Filtering on HTTP**: the VBS never travels over HTTP, it is written over SMB; read the capture in order.
- **Beacon jitter**: irregular intervals do not rule out C2; check the destination too.
