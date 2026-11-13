---
sherlock: Cuidado
category: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [soc, pcap, cryptominer, upx, bash, c2]
---

# Cuidado — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology writeup; no literal answers or real data.

## Scenario

The SOC detects abnormal CPU usage and outbound connections from a Linux server. A PCAP is provided to identify the download, the dropper and the miner being executed.

## Evidence

- PCAP of the server traffic.
- HTTP download identified in the capture.
- Shell script and a UPX-packed binary.
- C2 and mining-pool indicators.

```bash
capinfos capture.pcap
tshark -r capture.pcap -Y 'http.request' -T fields -e frame.time -e ip.src -e http.host -e http.request.uri
```

## Investigation

### 1. Inventory and triage

Obtain the time range, peers and protocols. HTTP downloads and high-port connections often explain the initial event.

```bash
tshark -r capture.pcap -q -z endpoints,ip
tshark -r capture.pcap -Y 'tcp.port == 80 || tcp.port == 443' -T fields -e http.host -e tls.handshake.extensions_server_name
```

### 2. Timeline

- First connection to the download server.
- Script execution and binary download.
- Start of periodic pool connections.
- Persistence through cron or a service.

PCAP timestamps are compared with the dropper file timestamps.

### 3. Key artefact

The shell script downloads a UPX-packed binary and executes it. After `upx -d`, strings reveal the miner, wallet and pool domain.

```bash
upx -d miner.bin -o miner.unpacked
strings -a miner.unpacked | grep -Ei 'pool|wallet|xmrig|stratum'
```

## Conclusions

- Initial access downloaded a dropper over HTTP.
- The dropper executed a UPX-obfuscated miner.
- Periodic traffic matches Stratum or the identified pool.
- IOCs: URL, hash, domain and port, redacted.

## Lessons

- Mining traffic can resemble legitimate HTTPS unless the SNI is reviewed.
- UPX remains a common obfuscation layer.
- Persistence must be checked even when the process is no longer running.

## References

- <https://www.hackthebox.com/sherlocks/Cuidado>
- <https://upx.github.io/>
- <https://attack.mitre.org/techniques/T1496/>
