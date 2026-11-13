---
challenge: Unique
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, can-bus, saleae, logic-analyzer, automotive]
---

# Unique — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A vehicle's differential signal is captured in a Saleae `.sal` file. The speed is not standard asynchronous serial: it is CAN at 125 kbps. Decoding the frames exposes the VIN and the flag in the data bytes.

## Prompt and surface

- Hardware, Easy, retired.
- `trace_captured.sal` is provided.
- The goal is to recover the VIN the vehicle repeatedly transmits.

```bash
file trace_captured.sal
7z l trace_captured.sal
```

## Reconnaissance

- The `.sal` is a compressed container with digital signals and metadata.
- Two complementary signals match CAN_H and CAN_L.
- UART decoding does not produce coherent characters.

```bash
unzip -l trace_captured.sal
```

## Analysis

1. Open the capture in Saleae Logic 2.
2. Measure the bit period: about 8 µs.
3. Compute `1 / 8 µs ≈ 125 kbps`.
4. Add the CAN analyser at 125000 bit/s.
5. Export frames and look for ASCII in the data field.

```text
bitrate = 1 / bit_time
125000 ≈ 1 / 8e-6
```

## Root cause

There is no software vulnerability: the challenge shows how a misread physical capture hides information. The correct protocol is CAN, not UART; the speed must be derived from the signal rather than assumed.

## Local reproduction

- Install Logic 2 and the CAN analyser.
- Load the `.sal` and select the differential channels.
- Try 125000, 250000 and 500000 bit/s.
- Export to CSV and filter printable bytes.

```bash
# After exporting the CSV
python3 - <<'PY'
import csv
for row in csv.reader(open("can.csv")):
    print("".join(chr(int(x, 16)) for x in row if 32 <= int(x, 16) < 127))
PY
```

## Evidence

- Bit-period measurement.
- CAN analyser configuration.
- Frames containing the VIN and flag, redacted.

## Lessons learned

- The physical layer determines which analyser makes sense.
- A wrong bitrate produces plausible but false data.
- `.sal` files can be inspected without the GUI.

## Mitigations and detection

- Segment and monitor vehicle CAN networks.
- Do not treat the VIN as authentication.
- Log anomalous frames and OBD-II bus access.
- Protect captures and device metadata.

## References

- <https://www.hackthebox.com/challenges/Unique>
- <https://www.saleae.com/downloads/>
- <https://en.wikipedia.org/wiki/CAN_bus>
