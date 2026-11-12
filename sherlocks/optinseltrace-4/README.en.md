---
sherlock: OpTinselTrace-4
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, pcap, printer, pjl, ssh, aes]
---

# OpTinselTrace-4 — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodological note; no literal answers.

## Scenario

The investigation reaches a print server. An AES-encrypted ZIP containing a network capture from the server is provided. Extract it, identify print traffic (PJL) and the SSH session, and reconstruct what was printed or exfiltrated.

## Evidence

- AES-encrypted ZIP (do not use `unzip`; use 7-Zip).
- `traffic.pcap`/`capture.pcapng` from the print server.
- PJL and SSH conversations.
- Possible print jobs and credentials.

```bash
7z x optinseltrace-4.zip
capinfos capture.pcap
```

## Investigation

### 1. Inventory and triage

Identify hosts and protocols:

```bash
tshark -r capture.pcap -q -z conv,tcp
tshark -r capture.pcap -Y 'pjl || ssh' -T fields -e frame.number -e ip.src -e ip.dst -e tcp.dstport
```

PJL usually uses port 9100; SSH uses 22. Separate the streams and reconstruct them.

### 2. Timeline

- Connection to the print server.
- PJL job with filename and user.
- SSH session and executed commands.
- Data transfer or printing of a sensitive document.

```bash
tshark -r capture.pcap -q -z follow,tcp,ascii,<STREAM>
```

### 3. Key artefact

The PJL stream holds the job name and sometimes cleartext content. The SSH session may include credentials or copy commands. The AES ZIP requires 7-Zip; `unzip` fails with “unsupported compression method”.

```text
AES ZIP -> PCAP -> PJL (job) + SSH (access)
```

## Findings

- The print server was used to print or extract a document.
- The SSH session allowed commands on the server.
- IOCs are IPs, ports, job name, user and path.
- ZIP encryption is only a transport layer, not evidence protection.

## Lessons

- 7-Zip handles AES; `unzip` does not.
- PJL can expose job names and content.
- SSH in a capture allows command reconstruction if not encrypted with an unknown key.
- Print servers are a common blind spot.

## References

- <https://inksec.io/blue-team/sherlocks/optinseltrace-4>
- <https://www.7-zip.org/>
- <https://attack.mitre.org/techniques/T1052/>
