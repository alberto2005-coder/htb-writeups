---
topic: CAN bus
tags: [hardware, automotive, can, logic-analyzer, saleae]
---

# CAN bus

**English** | [🇪🇸 Español](can-bus.md)

## Concept

Controller Area Network (CAN) is a differential bus used in vehicles and industrial systems. Nodes share CAN_H and CAN_L signals and transmit frames with an identifier and up to eight data bytes. Automotive networks commonly use 500 kbps, but 125 and 250 kbps are also common.

## When it applies

- Analysing logic-analyser captures.
- Diagnosing a vehicle or control network.
- Challenges with `.sal`, `.csv` or bus traces.
- Investigating message or sensor manipulation.

## Requirements and conditions

- Physical access or a capture of the differential signals.
- Knowledge of the bitrate.
- A CAN analyser or decoder supporting the format.
- Manufacturer documentation to interpret identifiers and signals.

## Procedure

1. Open the capture in a logic analyser.
2. Measure the bit period and calculate the bitrate.
3. Configure the CAN analyser at that bitrate.
4. Export frames with identifier, length and data.
5. Filter by identifier and look for ASCII or known signals.
6. Compare with vehicle or device documentation.

```text
bitrate = 1 / bit_time
125000 ≈ 1 / 8e-6
```

## Variants

- Classical CAN and CAN-FD.
- UDS over CAN for diagnostics.
- OBD-II as an access interface.
- LIN, FlexRay and automotive Ethernet in modern networks.

## Limitations

- A wrong bitrate produces plausible but false data.
- Identifiers and byte meanings are manufacturer-specific.
- Captures do not always include physical context.
- The bus was not designed with authentication or confidentiality.

## Mitigation

- Segment the network and use gateways between domains.
- Authenticate critical messages where the standard allows.
- Restrict access to the OBD-II port.
- Monitor unknown identifiers and abnormal frequencies.

## Detection

- Alert on unknown identifiers or altered frame rates.
- Detect message injection and replay.
- Correlate with physical and diagnostic events.
- Log bus access and firmware changes.

## References

- <https://en.wikipedia.org/wiki/CAN_bus>
- <https://www.saleae.com/downloads/>
- <https://attack.mitre.org/techniques/T1548/>
