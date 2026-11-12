---
topic: RDP bitmap cache
tags: [forensics, windows, rdp, bitmap-cache, bmc-tools]
---

# RDP bitmap cache

**English** | [🇪🇸 Español](rdp-bitmap-cache.md)

## Concept

The RDP client stores tiles of the remote screen to speed up drawing. These files (`Cache*.bin`, `bcache*.bmc`) survive session close and may contain text, documents and images the user saw. `bmc-tools` extracts the tiles and reconstructs the screen.

## When it applies

- A Windows user profile has an RDP cache.
- Investigating a remote session or an insider.
- Recovering visual content not present in history.
- The host has not been cleaned after the session.

## Requirements and conditions

1. Access to the profile's cache files.
2. `bmc-tools` and an image viewer.
3. Time to order tiles if the collage is misplaced.
4. Forensic copy; do not modify originals.

## Procedure

Locate the cache:

```text
C:\Users\<USER>\AppData\Local\Microsoft\Terminal Server Client\Cache\
C:\Users\<USER>\AppData\Local\Microsoft\Windows\INetCache\
```

Extract tiles:

```bash
git clone https://github.com/ANSSI-FR/bmc-tools
python3 bmc-tools/bmc-tools.py -s . -d bitmaps
```

Convert and review:

```bash
mkdir png
mogrify -format png bitmaps/*.bmp
```

`-b` builds a collage; if the order is wrong, manually order tiles containing text.

## Variants

- **RdpCacheStitcher**: GUI for ordering tiles.
- **Multiple sessions**: `Cache0000.bin`, `Cache0001.bin`, etc.; separate by session.
- **`bcache*.bmc`**: client bitmap cache; may be empty.
- **Virtual desktops**: the cache may contain several screens.

## Limitations

- Tiles do not always preserve original order.
- The cache is partial: only what was drawn.
- Content may be compressed or encrypted by the RDP version.
- Quality can be low; small text is hard to read.

## Mitigation

- Clear the RDP cache after sensitive sessions.
- Apply retention and secure-deletion policies.
- Restrict profile access and use managed devices.
- Avoid RDP to sensitive data from shared hosts.

## Detection

- Anomalous access to `Cache*.bin`/`bcache*.bmc`.
- Cache-extraction tools on the endpoint.
- RDP sessions outside hours or from unusual hosts.
- Unusual file volume in the cache directory.

MITRE ATT&CK: T1005 (Data from Local System), T1078 (Valid Accounts).

## References

- <https://github.com/ANSSI-FR/bmc-tools>
- <https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/rds-client-features>
- <https://attack.mitre.org/techniques/T1005/>
