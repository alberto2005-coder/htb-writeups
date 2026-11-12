---
challenge: Infiltration
type: OSINT
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [osint, linkedin, instagram, dorks, social-media]
---

# Infiltration — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The goal is to break into “Evil Corp LLC”. Searching the company on LinkedIn leads to its profile and an employee; their Instagram has a photo with a visible badge/note. Zooming in reveals the flag.

## Brief and surface

- OSINT, Easy, retired.
- No binary or service.
- Only the company name and objective are given.

## Recon

Search the company on a search engine and LinkedIn:

```text
"Evil Corp LLC" site:linkedin.com
```

The company profile shows a post with a base64-looking string. Decoding it gives an encouraging message, not the flag.

## Analysis

Identify employees and public profiles. One has an open Instagram. Review posts and look for images with text, whiteboards, badges or notes.

```bash
# Download the image and review metadata/zoom
exiftool photo.jpg
```

The flag is on a badge visible when one photo is enlarged.

## The bug

The company and employees publish sensitive information on social media: names, locations, badges and notes. Passive OSINT reconstructs access without touching systems.

## Local reproduction

1. Search the company on LinkedIn.
2. Enumerate employees and public profiles.
3. Review Instagram and image posts.
4. Zoom into the image and read the badge.

## Evidence

- Company profile screenshot with the base64 string.
- Instagram post with the relevant area cropped.
- Redacted flag.

## Lessons learned

- LinkedIn is a key source for org structure and employees.
- Photos can leak badges, notes and locations.
- Passive OSINT does not require contacting the victim.
- A base64 string may be a hint, not the secret.

## Mitigation and detection

- Social-media policies and post review.
- Blur badges and notes in corporate photos.
- Limit employee and site visibility.
- Social-engineering awareness training.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/osint/infiltration/>
- <https://osintframework.com/>
- <https://attack.mitre.org/techniques/T1593/001/>
