# Hardware: UART, firmware and extraction

**English** | [🇪🇸 Español](uart-firmware.md)

Note for Hardware challenges and for analysing a real embedded device: how to read the console and how to open the firmware.

## 1. Identify the board

- Silkscreen: model, revision and sometimes the pads (`TX`, `RX`, `GND`, `3V3`).
- Chips: SoC, SPI flash (Winbond, Macronix) and sometimes a debug header (JTAG/SWD).
- Look up the `FCC ID` and check the FCC internal photos database.

## 2. UART

| Signal | How to find it |
|---|---|
| GND | continuity with the chassis or the connector's negative |
| VCC | 3.3 V or 5 V with a multimeter; do not connect yet |
| TX | idle high, toggles during boot |
| RX | idle high; receives what you send |

```bash
ls /dev/ttyUSB*
picocom -b 115200 /dev/ttyUSB0
```

- Try `115200`, `57600`, `38400`, `9600`; on newer boards also `921600` and `4000000`.
- Adapter `TX` → board `RX`; common `GND`; **never** the adapter's `VCC` if the board is powered.
- **3.3 V** logic; 5 V can damage the SoC.

## 3. Boot

- U-Boot: interrupt at start and try `printenv`, `bootargs`, `init=/bin/sh`.
- Kernel: check the command line and console (`console=ttyS0,115200`).
- Login: `root`/`admin` with the rootfs password or one from a boot script.

## 4. Firmware

```bash
file firmware.bin
binwalk firmware.bin
binwalk -e --run-as=root firmware.bin
unblob firmware.bin
```

- `binwalk` recognises SquashFS, JFFS2, UBIFS, LZMA, gzip and partition tables.
- If it extracts nothing, find magic bytes by hand (`hsqs`, `UBI#`, `\x1f\x8b`) and cut with `dd`.
- Mount: `unsquashfs -d rootfs <image>` or `ubireader_extract_images`.

## 5. Inside the rootfs

```bash
grep -R -n -i "password\|passwd\|admin" rootfs/etc rootfs/usr 2>/dev/null | head
cat rootfs/etc/shadow
find rootfs -name "*.sh" -o -name "*.conf" | head
```

- Boot scripts with cleartext credentials.
- SSH keys and certificates.
- Exposed services (`telnetd`, `dropbear`, `httpd`) and their configs.

## 6. Direct flash read

Without UART:

- **SPI**: SOIC-8 clip and `flashrom -p ch341a_spi -r dump.bin`.
- **eMMC**: `mmc-utils` or an adapter; sometimes `CLK/CMD/DAT0` points exist.
- **JTAG/SWD**: OpenOCD with the SoC config.

## Typical errors

- **Garbage on the console** → bad `GND` or wrong baud; not the board.
- **No output** → `TX`/`RX` swapped or the console disabled in firmware.
- **`binwalk` does not recognise it** → encrypted image or proprietary LZMA; use `unblob` or custom signatures.
- **Boot verifies a signature** → rootfs cannot be modified; look for the console or bootloader.

MITRE: T1542.001, T1552.001, T1005.
