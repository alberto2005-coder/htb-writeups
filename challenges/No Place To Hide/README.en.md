---
challenge: No Place To Hide
type: Forensics
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [forensics, rdp, bitmap-cache, bmc-tools, image-reconstruction]
---

# No Place To Hide — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real flag.

## TL;DR

RDP cache files from a session (`Cache0000.bin` and `bcache24.bmc`) are provided. `bmc-tools` extracts over a thousand BMP tiles; converting and joining them reconstructs the screen the user saw, including the flag.

## Brief and surface

- Forensics, Easy, retired.
- RDP bitmap-cache files.
- The context is a password-spray attack and a suspicious RDP session.

```bash
file Cache0000.bin bcache24.bmc
du -h Cache0000.bin bcache24.bmc
```

`bcache24.bmc` may be empty; the useful evidence is in `Cache0000.bin`.

## Recon

The RDP cache stores screen tiles to speed up drawing. It is not a full image: extract the tiles and rebuild their position.

```bash
git clone https://github.com/ANSSI-FR/bmc-tools
python3 bmc-tools/bmc-tools.py -s . -d bitmaps
```

The tool reports over 1,000 extracted tiles.

## Source analysis

`bmc-tools` parses the BMCache format and exports each tile as BMP. The `-b` option builds a collage of all tiles, but the order may not match the original.

```bash
python3 bmc-tools/bmc-tools.py -s . -d bitmaps -b
```

## The bug

The cache preserves visual content even without a screenshot. An attacker with profile access can read sensitive data the user saw, and an analyst can reconstruct it. Deleting the image does not delete the cache.

## Local reproduction

```bash
mkdir png
mogrify -format png bitmaps/*.bmp
```

Review tiles and the collage. Zoom into text areas and order them manually if the collage is misplaced.

## Exploitation

There is no remote exploit. “Exploitation” is visual reconstruction: find tiles with characters and join them until the flag is readable. Verify it on the platform and redact it.

## Evidence

- `file` output for the cache files.
- Number of extracted tiles.
- Collage with the sensitive area blurred.

## Lessons learned

- The RDP cache retains session text and images.
- `bmc-tools` is the standard tile extractor.
- The collage does not always preserve order; review manually.
- Visual evidence can outlive the session.

## Mitigations and detection

- Clear the RDP cache after sensitive sessions.
- Restrict physical and logical access to the profile.
- Use remote desktops with minimal retention policies.
- Detection: anomalous access to `Cache*.bin` and bitmap cache.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/forensics/no-place-to-hide/>
- <https://github.com/ANSSI-FR/bmc-tools>
- <https://learn.microsoft.com/en-us/windows-server/remote/remote-desktop-services/rds-client-features>
