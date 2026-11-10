---
challenge: Bare Metal
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, avr, firmware, bit-bang, disassembly]
---

# Bare Metal — Hack The Box (Challenge)

[🇬🇧 English](README.en.md) | **Español**

## TL;DR

Firmware dump of an AVR microcontroller in Intel HEX format. There is no OS and no console: the program bit-bangs data out of a pin. Disassemble with `avr-objdump`, identify the two instructions that encode each bit, and rebuild the stream into the flag.

## Statement and surface

You get the firmware dump of a microcontroller and must work out what it transmits. Category Hardware, difficulty Easy.

## Recon

```bash
file firmware.hex
head -3 firmware.hex                  # Intel HEX format (:10....)
avr-objdump -D -m avr firmware.hex | head -60
```

## Code analysis

- The dump is not a rootfs: `binwalk` extracts nothing and there is no partition table.
- The disassembly shows a short loop with two instructions toggling an output pin: bit-bang pattern.
- The rest of the firmware is padding; the bit sequence is the message.

## Root cause

No vulnerability: this is firmware reversing. The wrong assumption is treating every dump as a Linux image; here the data lives in program logic, not in a filesystem.

## Local reproduction

```bash
avr-objdump -D -m avr firmware.hex > disasm.txt
# if the dump arrives as raw binary:
avr-objdump -D -b binary -m avr firmware.bin
```

## Exploitation

1. Find the loop writing the pin (`OUT`, `SBI`/`CBI` on `PORTx`).
2. Map each iteration to `0` or `1` depending on which of the two instructions opens it.
3. Group into bytes (MSB or LSB first, per the loop) and decode as ASCII.

```python
bits = [1, 0, 1, 0]        # taken from the disassembly
data = bytes(int("".join(map(str, bits[i:i+8])), 2) for i in range(0, len(bits) - 7, 8))
print(data)
```

## Evidence

- `avr-objdump` with the pin-writing loop.
- Bit and byte sequence rebuilt into readable text.

## Lessons

- **"Firmware" is not always a Linux image**: a microcontroller `.hex` is read by disassembling, not with `binwalk`.
- **Two instructions are enough to leak a message**: bit-bang leaves the data in write order.
- **Bit order matters**: try MSB and LSB before giving up on the stream.

## Mitigations and detection

- Protect physical access and the debug port against firmware reads.
- Sign firmware and verify the signature at boot; encrypt distributed binaries.

## References

- [MITRE T1542.001](https://attack.mitre.org/techniques/T1542/001/)
- [MITRE T1552.001](https://attack.mitre.org/techniques/T1552/001/)
