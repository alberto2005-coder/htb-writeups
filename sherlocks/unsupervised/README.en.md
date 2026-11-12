---
sherlock: Unsupervised
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, windows, registry, usb, jumplists, thumbcache]
---

# Unsupervised — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation note; no literal platform answers.

## Scenario

A suspect employee has been copying information out of the company. A triage of their Windows workstation is provided: registry hives, jump lists, thumbnail cache and device artefacts. The task is to determine which USB drive was connected, when, which files were opened or copied and what visual evidence remains.

## Evidence

- `C:\Users\<USER>\NTUSER.DAT` and `UsrClass.dat`.
- `C:\Windows\System32\config\SYSTEM` (for `USBSTOR` and `MountedDevices`).
- `AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations\*.automaticDestinations-ms`.
- `AppData\Local\Microsoft\Windows\Explorer\thumbcache_*.db`.
- `AppData\Local\Microsoft\Windows\Explorer\` and `ShellBags`.
- `C:\Windows\INF\setupapi.dev.log`.

```bash
sha256sum NTUSER.DAT UsrClass.dat SYSTEM setupapi.dev.log
```

Work on copies. Load hives in Registry Explorer or with `reg.py`; never mount them into the analysis host's registry.

## Investigation

### 1. Inventory and triage

Identify the profile and review device artefacts. The first question is whether a USB connection occurred and what identifier it has.

```bash
grep -a -i "USBSTOR\|RemovableMedia\|Disk&Ven" SYSTEM | head
```

`SYSTEM\CurrentControlSet\Enum\USBSTOR` holds vendor, product and serial number. `MountedDevices` maps the mounted drive (`\DosDevices\E:`) to the volume. `setupapi.dev.log` preserves the first device installation time.

### 2. Timeline

Cross:

- First USB connection (`setupapi.dev.log` and `USBSTOR`).
- `MountPoints2` entries in `NTUSER.DAT` with the volume GUID.
- File opens in jump lists and `RecentDocs`.
- ShellBag activity per folder.
- Thumbnails generated when images or documents were previewed.

Parse `AutomaticDestinations` jump lists with JLECmd, ShellBags with ShellBags Explorer and thumbcache with ThumbCache Viewer. Normalise times (some artefacts store UTC, others local time) and check the system zone.

### 3. Key artifact

The artifact that closes the case combines three pieces:

1. The USB serial in `USBSTOR`.
2. The volume GUID in `MountPoints2`.
3. A jump-list entry or thumbnail pointing to the sensitive file.

The jump list proves the user opened the file from a removable-drive path; the thumbnail proves the content was displayed on the host. Correlation with `setupapi.dev.log` places the connection in time.

```text
USBSTOR\Disk&Ven_<VENDOR>&Prod_<PRODUCT>&Rev_<REV>
<VOLUME_GUID> -> \??\Volume{...}\
```

## Findings

- A USB drive identifiable by serial number was connected.
- The user opened or copied files from that drive within a specific time window.
- Jump lists and the thumbnail cache preserve evidence of the content even if the file is gone.
- IOCs are the device serial, volume GUID and file paths.

## Lessons

- `USBSTOR` proves the connection; on its own it does not prove data was copied.
- Jump lists and ShellBags provide the “who opened what”.
- The thumbnail cache can preserve an image of a document even after deletion.
- Correlating three independent artefacts is stronger than any single answer.
