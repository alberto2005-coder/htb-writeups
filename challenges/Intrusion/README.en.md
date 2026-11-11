---
challenge: Intrusion
category: Challenge
type: ics
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [ics, scada, modbus, pcap, umodbus, plc]
---

# Intrusion — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method writeup; no real flags or credentials.

## TL;DR

A Modbus capture from an intrusion plus a live plant to connect to. The capture yields the register numbers the attacker queried and the `unit id` (52); part two is reading those holding registers in order from the instance and rebuilding the flag. Pure analysis is not enough: you have to speak Modbus.

## Statement and surface

- **ICS** category, **Easy** difficulty; Business CTF 2023.
- Download `ics_intrusion.zip` with `network_logs.pcapng` and a Docker instance of the Modbus plant.
- Scenario: after reaching the enemy infrastructure, traffic from their Modbus network was captured; find the registers holding sensitive data and extract it.

## Recon

- The capture is Modbus/TCP against port 502.
- The `unit id` in the requests is **52**.
- The read `reference numbers` point at the holding registers of interest.

The instance exposes a simulated PLC; the client connects to `127.0.0.1:502` from the challenge machine.

## Code analysis

There is no binary, but the PDF describes ladder logic: registers are not independent, they represent valves, sensors and states. The capture shows which addresses the attacker touched and in what order.

The flag is rebuilt by reading those registers in capture order and turning each 16-bit value into a character. One register per character is the usual convention; if a value is not printable, check whether you are reading the right register or whether the byte sits in the high half.

## Root cause

The PLC accepts unauthenticated reads from any host that can reach port 502. The attacker exploits no CVE: they use the protocol as designed. The lesson is that OT surface often trusts network segmentation, not authentication.

## Local reproduction

With the instance running, a minimal `umodbus` or `pymodbus` client:

```python
from pymodbus.client import ModbusTcpClient

c = ModbusTcpClient("127.0.0.1", port=502)
c.connect()
out = []
for addr in registers:             # extracted from the PCAP, in order
    rr = c.read_holding_registers(addr, count=1, slave=52)
    out.append(chr(rr.registers[0]))
print("".join(out))
c.close()
```

The `registers` list comes from the capture:

```bash
tshark -r network_logs.pcapng -T fields \
  -Y 'modbus.func_code == 3' -e modbus.reference_num | tr ',' '\n' | sort -n -u
```

## Exploitation

1. Extract the read `reference numbers` from the PCAP and sort them.
2. Confirm `unit id` 52.
3. Read each register from the instance.
4. Convert to ASCII and submit the flag.

## Evidence

- Register reads produce printable values spelling `HTB{...}`.
- Flag truncated in this writeup.

## Lessons learned

- In Modbus, `unit id` and address are part of the request; a wrong one returns an exception or another slave's data.
- The capture says *what* to read; the instance gives the *current* value. You need both.
- Automating the reads avoids 30 manual requests and ordering mistakes.

## Mitigations and detection

- Restrict port 502 to known masters and segment IT from OT.
- Detection: bulk sequential holding-register reads, new connections to the PLC, Modbus traffic from workstations.
- MITRE ATT&CK for ICS: T0846 (Remote System Discovery) and T0836 (Modify Parameter) as context.

## References

- <https://www.hackthebox.com/challenges/intrusion>
- <https://www.matthewdfurtado.com/blog/scada-intrusion>
- <https://medium.com/@biero-llagas/htb-ics-tracks-write-up-factory-watch-tower-and-intrusion-13065c1b0e93>
