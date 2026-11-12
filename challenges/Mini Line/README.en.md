---
challenge: Mini Line
type: Hardware
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [hardware, intel-hex, firmware, reversing, uart]
---

# Mini Line — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

Firmware is provided in Intel HEX format along with a serial capture. Convert the HEX to binary, identify the input-validation routine and reconstruct the sequence that prints the flag.

## Prompt and surface

- Hardware, Medium, retired.
- A `.hex` file and possibly a line capture are provided.
- No remote service.

```bash
file firmware.hex
head firmware.hex
```

## Reconnaissance

The file uses Intel HEX (`:LLAAAATT...CC`). Convert it to binary with `objcopy` or `srec_cat`:

```bash
objcopy -I ihex -O binary firmware.hex firmware.bin
```

Identify the architecture with `binwalk`/`strings` and load it into Ghidra/radare2.

## Analysis

1. Locate welcome strings and error messages.
2. Follow main and the comparison routine.
3. Identify the line protocol (ASCII commands, `\n` delimiter).
4. Reconstruct the expected input or emulate validation.
5. Extract the flag from memory or the response.

```bash
r2 -A firmware.bin
pdf @ main
```

## Root cause

Validation is implemented in extractable firmware and the key/flag is embedded or derivable. There is no cryptographic protection or integrity verification.

## Local reproduction

1. Convert Intel HEX to binary.
2. Identify architecture and entry point.
3. Analyse the comparison routine.
4. Emulate with `qemu` or rebuild the input.
5. Obtain the flag from the model.

## Evidence

- Original `.hex` and generated binary.
- Relevant strings and functions.
- Redacted flag.

## Lessons learned

- Intel HEX includes address and checksum per line.
- Firmware often contains messages that guide analysis.
- Emulation avoids running real hardware.
- Simple obfuscation does not protect secrets.

## Mitigation and detection

- Never store secrets in firmware.
- Sign and encrypt firmware.
- Protect debug bus access.
- Verify integrity at boot.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/mini-line/>
- <https://en.wikipedia.org/wiki/Intel_HEX>
- <https://ghidra-sre.org/>
