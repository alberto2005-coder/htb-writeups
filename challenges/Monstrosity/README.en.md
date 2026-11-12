---
challenge: Monstrosity
type: OSINT
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [osint, twitter, geolocation, social-media, api]
---

# Monstrosity — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A Twitter/X profile and its posts are investigated to geolocate a photograph. The key is correlating text, metadata and visual surroundings with mapping tools.

## Prompt and surface

- OSINT, Medium, retired.
- A username/profile and an image or clue are provided.
- No exploit files or instance.

## Reconnaissance

1. Archive the profile and list posts, followers and dates.
2. Extract image metadata (EXIF, software, GPS).
3. Look for city, event or business references.
4. Use reverse image search and maps.

```bash
exiftool image.jpg
```

## Analysis

- Identify landmarks: architecture, signage, vegetation, language.
- Narrow the country/city using text and skyline.
- Compare with Google Maps/Street View and satellite imagery.
- Confirm the location with independent sources.
- The flag comes from the location or a visible object.

> **Limitation:** the old Twitter API is no longer available; the flow is documented with files and screenshots.

## Root cause

Combining a public profile, images with intact metadata and geographic text allows locating a person or place without technical access.

## Local reproduction

1. Save profile screenshots.
2. Review EXIF and metadata.
3. Run reverse image search.
4. Cross-check with maps.
5. Write the conclusion and flag.

## Evidence

- Profile and post screenshots.
- `exiftool` output.
- Map comparison.
- Redacted flag.

## Lessons learned

- Text and images complement each other.
- Metadata can remove the need for geolocation.
- Confirmation needs several sources.
- APIs change; archive.

## Mitigation and detection

- Strip EXIF before publishing.
- Check photo backgrounds.
- Limit profile visibility.
- Do not post real-time locations.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/osint/monstrosity/>
- <https://exiftool.org/>
- <https://www.google.com/maps/>
