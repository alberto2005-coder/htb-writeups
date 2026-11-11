---
challenge: Watch Tower
category: Challenge
type: ics
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [ics, scada, modbus, pcap, tshark]
---

# Watch Tower — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method writeup; no real flags or credentials.

## TL;DR

A traffic-analysis challenge: a `pcapng` full of Modbus/TCP where someone wrote to a slave. The flag is not in the written values but in the **reference numbers** of the `Write Multiple Registers` (function 16) requests: as ASCII they spell `HTB{...}`. One `tshark` filter plus `awk` solves it.

## Statement and surface

- **ICS** category (also listed as Hardware/SCADA), **Very Easy** difficulty.
- Business CTF 2023; the download is `ics_watch_tower.zip`, containing `tower_logs.pcapng`.
- No service to attack: the whole job is on the capture.

## Recon

`Statistics → Protocol Hierarchy` shows Modbus/TCP only. The function codes present are:

| Code | Function | Role in the capture |
|---:|---|---|
| 1 | Read Coils | Verification reads |
| 15 | Write Multiple Coils | Initial coil write (no useful ASCII) |
| 16 | Write Multiple Registers | 57 writes: the data is here |

The master is `192.168.1.150`; the slave answers from port 502.

## Code analysis

There is no binary. In Modbus/TCP each PDU follows the MBAP header (transaction id, protocol id, length, unit id), and function 16 carries:

- **Reference Number**: the starting register of the write.
- **Word Count** and **Register Value**: how many registers and their contents.

Here the values are noise, but the reference numbers run 72, 84, 66, 123… which are ASCII `H`, `T`, `B`, `{`. The flag lives in the addressing, not the payload.

## Root cause

The scenario says the attacker "collected and altered" information. The alteration is in the addresses: using the register number as a covert channel lets data be written while the values look unremarkable. This is **metadata as a channel**, not a protocol bug.

## Local reproduction

```bash
tshark -r tower_logs.pcapng -T fields \
  -Y 'ip.src == 192.168.1.150 && modbus.func_code == 16' \
  -e modbus.reference_num \
  | awk '{for (i = 1; i <= NF; i++) printf "%c", $i}'
```

Wireshark alternative: filter `modbus.func_code == 16`, add a `modbus.reference_num` column and export the dissections.

## Exploitation

1. Open the capture and confirm it is Modbus/TCP only.
2. Filter function 16 from the master.
3. Extract `modbus.reference_num` and convert to ASCII.
4. Submit the resulting string.

## Evidence

- The decoded sequence starts with the flag prefix and ends with the closing brace.
- Flag truncated in this writeup.

## Lessons learned

- In Modbus, address and value are separate fields; looking only at values misses half the traffic.
- `modbus.reference_num` (register) is not `modbus.regval_uint16` (content).
- `tshark -T fields` turns a capture into a table that shell tools can process.
- A covert channel can use addresses, timing or sizes, not just payloads.

## Mitigations and detection

- Modbus/TCP has no authentication or encryption: segment the network, allowlist masters and passively monitor port 502.
- Detection: writes outside the usual register map, ascending address sequences, and Modbus traffic from non-SCADA hosts.
- MITRE ATT&CK for ICS: T0836 (Modify Parameter) and T0842 (Network Sniffing) as context.

## References

- <https://www.hackthebox.com/challenges/watch-tower>
- <https://7rocky.github.io/en/ctf/htb-challenges/ics/watch-tower/>
- <https://www.matthewdfurtado.com/blog/scada-watchtower>
- <https://sud0ru.ghost.io/ics-security-series-part-1>
