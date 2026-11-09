---
challenge: Deadly Arthropod
category: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, usb, hid, pcap, keystrokes]
---

# Deadly Arthropod — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

The capture contains **USB traffic from a keyboard**. Each press travels as an 8-byte HID report; rebuilding the *keycode* sequence reads back the typed text, which is the flag. The catch is the keymap and the uppercase letters.

## Evidence

- A USB traffic capture (`usb.pcapng`).

## Method

1. **Isolate the device**: identify the keyboard's address and its interrupt endpoint.

```bash
tshark -r usb.pcapng -Y 'usb.transfer_type == 0x01' -T fields -e usb.src -e usb.dst | sort | uniq -c
```

2. **Pull the HID reports**: byte 0 is the modifier (Shift), byte 2 is the pressed key's *keycode*.

```bash
tshark -r usb.pcapng -Y 'usb.capdata' -T fields -e usb.capdata
```

3. **Translate**: with the HID Usage ID table each keycode becomes a character; `0000000000000000` reports are releases (skip them) and modifier `02` or `20` means Shift.

```python
# skeleton: read capdata, skip empty, map keycode -> char
```

4. **Read the output**: the sequence spells the typed text with the flag. Verify order and capitalisation character by character.

## Pitfalls

- **Empty reports**: unless filtered, every key appears twice (press and release).
- **Shift**: ignoring it yields a lowercase flag the validator rejects.
- **Repeats**: two identical reports in a row are one held key; decide whether it counts once or twice.
- **Layout**: the HID map is US; if the expected text does not line up, recheck the mapping (`-`, `_`, `{`, `}`).

## Lessons

- Unencrypted USB traffic exposes what is typed: keyboards, controllers and readers.
- HID reports are a fixed, simple format; a 20-line script is enough.
- One badly mapped character invalidates the flag: validate the rebuild step by step.
