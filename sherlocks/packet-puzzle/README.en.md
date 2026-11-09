---
sherlock: Packet Puzzle
domain: DFIR / Network
difficulty: Medium
platform: Hack The Box
evidence: PCAP from a cryptocurrency company
tools: [Wireshark, tshark, NetworkMiner, CyberChef]
---

# Packet Puzzle — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

A small Japanese cryptocurrency exchange notices suspicious activity on its internal network and exports a PCAP. Determine whether the environment was compromised and rebuild the attacker's steps.

## Evidence

- `NetworkTraffic.pcap` inside the usual ZIP.

## Method

1. **Reconnaissance**: count the ports the source touches and how many answer.

```bash
tshark -r NetworkTraffic.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' \
  -T fields -e ip.src -e ip.dst -e tcp.dstport | sort -u | wc -l
```

A sweep across several services (RDP, SMB, HTTP/S, WinRM and a printing one) confirms discovery scanning.

2. **Entry service**: the first port that responds and the protocol used afterwards. In this capture access ends on **RDP**, with credential attempts.

```bash
tshark -r NetworkTraffic.pcap -Y 'tcp.port==3389' -T fields -e ip.src -e ip.dst | sort | uniq -c
```

3. **Interactive session**: after access a shell appears; commands (`whoami`, disk enumeration) and their output travel in cleartext over the channel.

4. **Movement and collection**: new internal SMB streams, mounted shares and data copied to the attacker host.

5. **Timeline**: `frame.time` of the first service reply, the successful login and the first data transfer.

## What it teaches

- Tell *scan* from *exploitation*: scanning is symmetric and short; exploitation produces a session and data.
- RDP reveals the operating system and, with weak credentials, is a direct door in.
- A PCAP ordered by time tells the whole story without host logs.

## Pitfalls

- **Many ports, few packets**: do not mistake a fast sweep for a successful exploit.
- **Long sessions**: RDP streams are heavy; filter on one `tcp.stream`.
- **Encodings**: stolen data may be compressed or base64; try `Export Objects` before decoding by hand.
