---
challenge: Shush Protocol
category: Challenge
type: ics
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [ics, modbus, pcap, wireshark, custom-function-code]
---

# Shush Protocol — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method writeup; no real flags or credentials.

## TL;DR

A Modbus/TCP PCAP where the control device speaks a proprietary protocol with **function code 102**, which does not exist in the standard. Following the TCP stream of those packets and reading the hex dump reveals the user `operator` and their password, which is the flag. Nothing is exploited: the traffic just has to be read.

## Statement and surface

- **ICS** category, **Very Easy** difficulty; Business CTF 2024.
- Download `ics_shush_protocol.zip`, containing `traffic.pcapng`.
- The goal is the password the control device uses to talk to the PLC.

## Recon

- All traffic is Modbus/TCP on port 502.
- Most packets use standard functions, but several carry function **102**: a proprietary code.
- Most of those are diagnostic noise; a single one transports an unusually large amount of data.

## Code analysis

There is no binary or instance. The "code" is the protocol: function 102 wraps its own fields inside the Modbus PDU. Following the TCP stream and switching to `Hex Dump` shows that the large packet writes a string with the user and the password in clear text.

Function 102 is absent from the Modbus function table, so Wireshark does not dissect it: the bytes have to be read directly.

## Root cause

The proprietary protocol adds no security: the password travels unencrypted and the client sends it to the PLC on every session. Obscurity of the function code does not protect the data, and a passive capture is enough to extract it.

## Local reproduction

```bash
# locate packets with the proprietary function
tshark -r traffic.pcapng -Y 'modbus.func_code == 102' -T fields -e data

# or open the TCP stream in Wireshark: Follow → TCP Stream → Show data as Hex Dump
```

Convert the hex dump with `xxd -r -p` or CyberChef's `From Hex`.

## Exploitation

1. Open the capture and filter `modbus.func_code == 102`.
2. Follow the TCP stream of the packet with the most data.
3. Switch to hex and decode to ASCII.
4. Submit the password found.

## Evidence

- The dump shows the user `operator` followed by a password in flag format.
- Flag truncated in this writeup.

## Lessons learned

- Function codes above the standard range usually mean proprietary protocols.
- A single anomalous packet can hold everything; sorting by length helps.
- Following the TCP stream is more reliable than reading single packets when the PDU is fragmented.
- "Proprietary protocol" does not mean "encrypted".

## Mitigations and detection

- Never send credentials in clear text: mutual authentication and tunnels on the OT segment.
- Detection: non-standard function codes, large writes from a diagnostic host and new connections to the PLC.
- MITRE ATT&CK for ICS: T0842 (Network Sniffing) and T0836 (Modify Parameter) as context.

## References

- <https://github.com/hackthebox/business-ctf-2024/tree/main/ics/Shush%20Protocol%20%5BVery%20Easy%5D>
- <https://www.matthewdfurtado.com/blog/ics_shushprotocol/>
- <https://medium.com/@a19941006/htb-ctf-shush-protocol-9c134bd8ea13>
