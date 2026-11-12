---
challenge: Secure Digital
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, spi, microsd, logic-analyzer, file-carving]
---

# Secure Digital — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The SPI bus of a microSD card is captured with a logic analyser. Decoding MISO/MOSI/CLK/CS reconstructs the sector read and extracts the image; the flag is inside.

## Prompt and surface

- Hardware, Easy, retired.
- A logic-analyser capture (`.sal`/`.logicdata`) or SPI dump is provided.
- No remote service.

```bash
file secure_digital.sal
```

## Reconnaissance

Open the capture in Logic 2/Saleae. Four channels are visible: `CLK`, `CS`, `MOSI` and `MISO`. The card answers in SPI mode after `CMD0`/`CMD8`.

## Analysis

1. Add the SPI analyser with `CS` active low and sample on the correct edge.
2. Set bit order (MSB) and word size (8 bits).
3. Export the MISO bytes.
4. Rebuild the `CMD17` (single-block read) sequence and returned data.
5. Concatenate blocks and look for a filesystem signature.

```bash
binwalk -e sdcard.bin
strings -n 6 sdcard.bin | less
```

## Root cause

The capture exposes the card contents without encryption or authentication. The SPI bus is physically accessible and does not protect data at rest.

## Local reproduction

1. Open the capture and decode SPI.
2. Export MISO to binary.
3. Trim 512-byte blocks.
4. Mount or analyse the resulting image.

```bash
sudo mount -o loop,ro sdcard.bin /mnt/sd
```

## Evidence

- Original capture and analyser settings.
- Reconstructed image and `binwalk` output.
- Redacted flag.

## Lessons learned

- SPI is a simple synchronous bus to decode.
- `CS` delimits transactions.
- SD commands follow a predictable format.
- Physical extraction needs no credentials.

## Mitigation and detection

- Encrypt sensitive data on removable media.
- Use secure boot/firmware verification.
- Restrict physical access and seal ports.
- Audit media extraction.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/hardware/secure-digital/>
- <https://www.saleae.com/>
- <https://en.wikipedia.org/wiki/Serial_Peripheral_Interface>
