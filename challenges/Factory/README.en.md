---
challenge: Factory
category: Challenge
type: ICS
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [ics, scada, modbus, rtu, plc, ladder-logic]
---

# Factory — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Method writeup; no real flags or credentials.

## TL;DR

A water plant with the HMI down and the PLC halted because the level sensors are corrupted. Read the ladder-logic diagram, switch the PLC to manual and force the outlet valve to drain the tank before it overflows. This is Modbus RTU over the serial network the operative can reach, not an exploit.

## Statement and surface

- **ICS** category, **Easy** difficulty; Business CTF 2023.
- The download includes a PDF with the remote plant and the Modbus RTU map, plus the instance connection.
- The PLC has a slave on the serial network; the HMI no longer answers.

## Recon

- Identify the slave and medium: Modbus RTU over serial, through the gateway shown in the PDF.
- Read the diagram: which coil opens the inlet valve, which one the outlet, which enables manual mode and which starts the process.
- Check state: `auto_mode` on and the PLC halted by the corrupted level sensors.

## Code analysis

The PDF's ladder logic is the "code". It shows the PLC only drives the valves in manual; in auto, the corrupted sensors keep it halted. The sequence is:

1. Turn automatic mode off.
2. Enable manual mode.
3. Open the outlet valve (and close the inlet) with `Write Single Coil` (function 5).
4. Confirm with coil reads that the tank is draining.

The example slave is 52 and the outlet valve is forced with `FF 00` on its coil, per the PDF map.

## Root cause

No CVE: the PLC accepts coil writes without authentication from the field network, and safety logic trusts the sensors. The challenge shows the physical impact of a `Write Single Coil`: no data is exfiltrated, a valve moves.

## Local reproduction

With `mbpoll` against the serial gateway (set device and baud rate from the PDF):

```bash
mbpoll -m rtu -a 52 -b 9600 -P none -d 8 -s 1 -t 0 -r 5 /dev/ttyUSB0 0   # auto_mode off
mbpoll -m rtu -a 52 -b 9600 -P none -d 8 -s 1 -t 0 -r 6 /dev/ttyUSB0 1   # manual on
mbpoll -m rtu -a 52 -b 9600 -P none -d 8 -s 1 -t 0 -r 5 /dev/ttyUSB0 1   # outlet open
```

Coil numbers come from the PDF map; they are not copied here because they change per instance.

## Exploitation

1. Read the diagram and locate the mode and valve coils.
2. Write `auto_mode = 0` and `manual_mode = 1`.
3. Force the outlet valve and close the inlet.
4. Read state until the tank is empty; the platform validates and returns the flag.

## Evidence

- Mode and valve coils hold the expected values after the sequence.
- Flag truncated in this writeup.

## Lessons learned

- In ICS the objective can be physical: drain a tank, not read a file.
- Ladder logic is the specification; without reading it, writing coils is guessing.
- `Write Single Coil` uses `FF 00` for ON and `00 00` for OFF.
- Modbus RTU needs correct port parameters (baud, parity, stop bits) before any write.

## Mitigations and detection

- Protect manual mode with physical interlocks and authenticated gateways.
- Detection: auto-to-manual transitions, writes to valve coils, and commands from hosts outside the SCADA.
- MITRE ATT&CK for ICS: T0836 (Modify Parameter) and T0855 (Unauthorized Command Message).

## References

- <https://www.hackthebox.com/challenges/factory>
- <https://piyushs3v3n.github.io/HackTheBox-Factory-WriteUp>
- <https://medium.com/@biero-llagas/htb-ics-tracks-write-up-factory-watch-tower-and-intrusion-13065c1b0e93>
- <https://foobarto.me/htb/challenges>
