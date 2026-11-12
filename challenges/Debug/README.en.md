---
challenge: Debug
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, uart, logic-analyzer, serial, cyber-apocalypse]
---

# Debug — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A logic-analyser capture contains a UART line. Configuring the async serial analyser at 115200 baud decodes the boot log, and the console prints the flag.

## Prompt and surface

- Hardware, Easy, retired (Cyber Apocalypse 2023).
- `hw_debug.sal` is provided.
- No remote service.

```bash
file hw_debug.sal
```

## Reconnaissance

Open the capture in Logic 2. Two signals are present, `TX` and `RX`; only one shows activity. Identify the device's transmit pin.

## Analysis

1. Add the `Async Serial` analyser.
2. Try standard baud rates: 9600, 19200, 38400, 57600, 115200.
3. 115200 produces readable text.
4. Export the bytes and convert hex to ASCII.
5. The boot console prints the flag across several lines.

```bash
# Export bytes and decode
python3 -c "print(bytes.fromhex('...').decode(errors='replace'))"
```

You can also copy the text directly from the analyser and join the lines.

## Root cause

The UART debug console is accessible without authentication, exposing the boot process and secrets. There is no physical protection or port disablement.

## Local reproduction

1. Open the capture.
2. Add Async Serial on the active channel.
3. Set 115200 8N1.
4. Export/decode.
5. Rebuild the flag.

## Evidence

- Capture and analyser settings.
- Decoded text.
- Redacted flag.

## Lessons learned

- UART is a simple asynchronous serial protocol.
- The correct baud rate is key to decoding.
- Debug consoles often print secrets.
- Signal analysis does not require the hardware.

## Mitigation and detection

- Disable debug consoles in production.
- Physically protect UART pads.
- Never print secrets at boot.
- Sign/verify firmware.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/debug/>
- <https://www.saleae.com/>
- <https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter>
