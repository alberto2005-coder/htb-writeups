---
challenge: Bare Metal
type: Hardware
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [hardware, uart, firmware, binwalk, flash]
---

# Bare Metal — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

## Brief

You get a firmware image from an embedded device. Find the serial console and extract system information: credentials, services and the flag.

## Firmware triage

```bash
file firmware.bin
binwalk firmware.bin
binwalk -e firmware.bin
strings -a firmware.bin | grep -i -E "uart|console|baud|root|passwd"
```

`binwalk -e` separates the filesystem (SquashFS, JFFS2, UBIFS). On a full image you get the partition table, kernel and rootfs.

## UART console

1. **Find the pins**: `TX`, `RX`, `GND` (sometimes `VCC`) are usually labelled or grouped in a row of 3-4 pads. Identify `GND` by continuity with the chassis.
2. **Adapter**: USB-TTL at **3.3 V** (never 5 V without checking). Adapter `TX` to board `RX` and vice versa; common `GND`.
3. **Baud**: try `115200 8N1` first, then `57600`, `38400`, `9600`. With `picocom`:

   ```bash
   picocom -b 115200 /dev/ttyUSB0
   ```

4. **Boot**: U-Boot appears on power-up. If it allows `init=/bin/sh` or a console, you get a shell without credentials.
5. **Login**: if it asks for a user and password, look them up in the rootfs (`/etc/shadow`, `/etc/passwd`) after mounting.

## Extract from the rootfs

```bash
unsquashfs -d rootfs squashfs-root.squashfs
grep -R "password\|admin" rootfs/etc 2>/dev/null | head
cat rootfs/etc/shadow
```

With `/etc/shadow` and `john`/`hashcat` weak passwords fall; many images ship `root`'s password in cleartext inside boot scripts.

## Typical errors

- **No UART output** → `TX`/`RX` swapped or wrong baud; also try 4 Mbps on modern boards.
- **Garbage characters** → bad common ground or different logic level (1.8 V).
- **`binwalk -e` extracts nothing** → encrypted image or proprietary LZMA; use `unblob` or carve at the offsets.
- **Login rejected** → the password is in the rootfs; do not brute-force the console.

## Lessons

- Firmware usually gives up the password before the console does.
- `GND` first, then `TX`/`RX`; a wrong cable breaks nothing but yields no output.
- Modern images are signed: check whether boot verifies the signature.

MITRE: T1542.001, T1552.001.
