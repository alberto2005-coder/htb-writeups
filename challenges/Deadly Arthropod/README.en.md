---
challenge: Deadly Arthropod
category: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, usb, hid, pcap, keystrokes]
---

# Deadly Arthropod — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

The capture is **USB traffic from a keyboard** (the device descriptor identifies a **Razer BlackWidow Ultimate 2013**). Each press travels as an 8-byte HID report; filtering the 35-byte packets and dropping empty reports, the *keycode* sequence spells the typed text, which contains the flag. The catch is the keymap and the uppercase letters.

## Evidence

- `deadly_arthropod.pcap`, a capture of a single USB transfer with no network traffic.

## Method

1. **Isolate the device**: identify the keyboard's address and its interrupt endpoint.

```bash
tshark -r usb.pcapng -Y 'usb.transfer_type == 0x01' -T fields -e usb.src -e usb.dst | sort | uniq -c
```

2. **Pull the HID reports**: boot-protocol reports are 8 bytes, byte 0 is the modifier (Shift) and byte 2 the pressed key's *keycode*.

```bash
tshark -r deadly_arthropod.pcap -Y 'usb.transfer_type == 0x01 && frame.len == 35' \
  -T fields -e usb.capdata | grep -v '^0000000000000000$'
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

## Mitigation

There is no software bug here: the flaw is **physical**. A USB sniffer sees everything typed, flag included.

- Encrypt or block USB ports on sensitive machines, and use authenticated keyboards where the risk justifies it.
- Detection: USB captures with an unexpected HID device and keyboard activity outside a user session; on the endpoint, injected HID drivers.
- Operational rule: never type secrets on a host with a USB sniffer attached.

## Lessons

- Unencrypted USB traffic exposes what is typed: keyboards, controllers and readers.
- HID reports are a fixed, simple format; a 20-line script is enough.
- One badly mapped character invalidates the flag: validate the rebuild step by step.
