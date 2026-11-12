---
challenge: 0ld is g0ld
type: Misc
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [misc, pdf, john, morse, stego]
---

# 0ld is g0ld — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real password or flag.

## TL;DR

A password-protected PDF. `pdf2john` extracts the hash, `john` cracks it with `rockyou.txt`, and the PDF reveals a portrait with a strip of Morse code. Decoding it yields the flag.

## Brief and surface

- Misc, Easy, retired.
- `0ld is g0ld.pdf` is provided.
- The PDF asks for a password.

```bash
file '0ld is g0ld.pdf'
pdfinfo '0ld is g0ld.pdf'
```

## Recon

```bash
pdf2john '0ld is g0ld.pdf' > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

`pdf2john` produces a John-compatible hash. The password appears in the output; it is not published.

## Source analysis

There is no code: the challenge combines PDF cracking and visual steganography. Opening the document shows a portrait; zooming in reveals dots and dashes.

```bash
john --show hash.txt
```

## The bug

The PDF password is weak and in a common wordlist. Once opened, the message is hidden in the image, not in metadata or a separate layer. “Security” relies on two trivial layers.

## Local reproduction

```bash
xdg-open '0ld is g0ld.pdf'
```

Crop the Morse area and decode it with a table or an offline/online tool. The result matches HTB's flag format.

## Exploitation

There is no server. Exploitation is passive: crack, open, read Morse and decode. Verify it on the platform and redact it.

## Evidence

- `pdf2john` and `john --show` with the password redacted.
- Portrait screenshot with the Morse visible.
- Decoded text with the flag redacted.

## Lessons learned

- `pdf2john` + `john` is the standard flow for weak PDFs.
- Visual steganography needs no complex tooling.
- Zoom and contrast are enough to read the message.
- The PDF password does not protect content once cracked.

## Mitigations and detection

- Use strong passwords and AES-256 for sensitive PDFs.
- Do not hide secrets in images without additional encryption.
- Rotate any secret exposed in a PDF.
- Detection: bulk PDF access and `pdf2john`/`john` execution.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/misc/0ld-is-g0ld/>
- <https://www.openwall.com/john/>
- <https://en.wikipedia.org/wiki/Morse_code>
