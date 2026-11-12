---
challenge: Debugging Interface
type: Hardware
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [hardware, uart, saleae, logic-analyzer, serial]
---

# Debugging Interface — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

An embedded device's asynchronous serial interface (UART) is captured. The `.sal` file is a Saleae Logic ZIP containing `digital-0.bin` and `meta.json`. The shortest pulse gives 31250 baud; decoding the line as UART reveals the message with the flag.

## Brief and surface

- Hardware, Very Easy, retired.
- `debugging_interface_signal.sal` is provided.
- A single digital channel.

```bash
file debugging_interface_signal.sal
unzip -l debugging_interface_signal.sal
```

## Recon

```bash
unzip debugging_interface_signal.sal -d sal
ls sal
# digital-0.bin  meta.json
```

`digital-0.bin` does not follow Saleae's documented export format; interpret it as an edge trace. `meta.json` gives the sample rate (50 MS/s).

## Analysis

Load the `.sal` in Saleae Logic or parse `digital-0.bin` to rebuild edge timings. The shortest pulse is about 32 µs:

```text
bit = 1 / 31250 ≈ 32 µs
```

Configure the `Async Serial` decoder on channel 0 at 31250 baud, 8 data bits, no parity, 1 stop bit. The output is ASCII text containing the flag.

Alternative without Saleae:

```python
# Read edges, group by bit duration and sample 8 bits per character
```

## The bug

The UART debug interface remains accessible and transmits cleartext data, including sensitive information. There is no authentication or encryption on the serial link.

## Local reproduction

1. Extract the `.sal`.
2. Measure the bit period.
3. Decode as UART 31250 8N1.
4. Export the text and locate the flag pattern.

## Evidence

- `file`/`unzip` of the `.sal`.
- Period measurement and baud calculation.
- Decoded text with the flag redacted.

## Lessons learned

- UART is common in embedded debugging.
- Baud rate is derived from the shortest pulse.
- `.sal` files are ZIPs with binary data.
- Physical instrumentation can reveal secrets.

## Mitigation and detection

- Disable debug UART in production.
- Protect pads with a password or fuses.
- Never transmit secrets over serial interfaces.
- In the lab, document capture and baud rate.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/debugging-interface/>
- <https://support.saleae.com/>
- <https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter>
