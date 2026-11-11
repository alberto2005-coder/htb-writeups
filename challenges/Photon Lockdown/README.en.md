---
challenge: Photon Lockdown
category: Challenge
type: hardware
os: Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [hardware, firmware, squashfs, rootfs, iot, credentials]
---

# Photon Lockdown — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no real flags or credentials.

## TL;DR

Firmware for a home ONT: two version files and a SquashFS `rootfs` image. Extracting it reveals the default configuration with the superuser password in clear; that password is the flag. No binary to reverse: the flaw is shipping factory credentials inside the firmware.

## Prompt and surface

- **Hardware** category, **Very Easy** difficulty.
- Ships `fwu_ver`, `hw_ver` and `rootfs`.
- The goal is to gain access to the device from its firmware.

```bash
file fwu_ver hw_ver rootfs
cat fwu_ver hw_ver
```

```text
fwu_ver: 3.0.5
hw_ver:  X1
rootfs:  Squashfs filesystem, little endian, version 4.0, zlib
```

## Recon

```bash
binwalk rootfs
unsquashfs -l rootfs | head -30
```

`binwalk` confirms there are no hidden layers: a plain SquashFS. The listing shows a compact Linux tree with `/etc`, `/bin` and `/www`.

## Code analysis

```bash
unsquashfs rootfs
grep -ril "password\|passwd\|admin" squashfs-root/etc | head
```

The interesting file is `etc/config_default.xml`, which the device copies into its configuration on first boot. It holds the panel user and password:

```xml
<Value Name="SUSER_PASSWORD" Value="<HTB{...}>"/>
```

## Why it fails

The firmware ships the factory password in plaintext inside the image, and that password is unique per model. Anyone with the firmware can extract it and log in to every device that never changed it.

```bash
grep -r "SUSER_PASSWORD" squashfs-root/etc/
```

## Local reproduction

```bash
unsquashfs rootfs -d rootfs_out
grep -r "SUSER_PASSWORD" rootfs_out/etc/
# without extracting:
strings rootfs | grep -i "SUSER_PASSWORD"
```

## Exploitation

1. Extract the SquashFS.
2. Read `config_default.xml` and locate `SUSER_PASSWORD`.
3. Use that credential on the device panel (or submit it as the flag, as the challenge asks).

No firmware emulation or hardware is required.

## Evidence

- `file` on `rootfs` confirming SquashFS.
- `grep` output with the `SUSER_PASSWORD` line and the value redacted.

## Lessons learned

- Firmware is a filesystem: if it can be downloaded, it can be read.
- Factory credentials shared across a model are an open door for the whole fleet.
- `unsquashfs` and `strings` solve most of these challenges without `binwalk -e`.
- The firmware version (`fwu_ver`) is useful for model CVEs, though not needed here.

## Mitigations and detection

- Generate a per-device password on first boot and force a change.
- Never ship plaintext credentials in the image; use a per-unit secret or secure provisioning.
- Sign firmware and verify updates.
- Detection: panel logins with the default credential and devices that never changed the password.
- References: OWASP IoT Top 10 (I1 weak credentials), MITRE T1078.001.

## References

- <https://www.hackthebox.com/challenges/photon-lockdown>
- <https://0x42697262.github.io/birbrain/writeups/HackTheBox/photon_lockdown.html>
- <https://dua2z3rr.github.io/posts/Photon-Lockdown-Writeup>
- <https://github.com/plougher/squashfs-tools>
