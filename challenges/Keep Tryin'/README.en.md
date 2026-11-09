---
challenge: Keep Tryin'
category: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, pcap, dns-exfil, base64url, rc4]
---

# Keep Tryin' — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A **26-packet** PCAP with three things: a `POST /flag` carrying `TryHarder`, a `POST /lootz` with base64 ("Keep trying, buffy") and **DNS TXT queries whose subdomains are base64url**. The first subdomain decodes to `secret.txt|1`: DNS exfiltration. Concatenate the chunks, decrypt with **RC4** keyed on `TryHarder`, and a ZIP with `secret.txt` falls out.

## Evidence

- `keeptryin.pcap` inside a ZIP.

## Method

1. **See the whole thing**: it is small enough to read entirely.

```bash
tshark -r keeptryin.pcap -Y 'dns' -T fields -e dns.qry.name | head
```

```text
init.c2VjcmV0LnR4dHwx.totallylegit.com
```

2. **Decode the index**: `c2VjcmV0LnR4dHwx` in base64url is `secret.txt|1` → file name and part number.

3. **Collect the parts**: the remaining TXT records carry the chunks; sort by index and concatenate.

4. **Key**: the `POST`s provide the auxiliary material. `TryHarder` is the RC4 key; the `/lootz` base64 is just a hint.

```bash
# CyberChef: From Base64 (url safe) -> RC4 (key: TryHarder) -> Unzip
```

5. **Open** the resulting ZIP: `secret.txt` holds the flag.

## Pitfalls

- **base64 vs base64url**: the alphabet differs (`-` and `_`); plain base64 fails.
- **Part order**: without the subdomain index the ZIP comes out corrupt.
- **Noise**: none here; on a larger capture filter `dns.qry.type == 16` (TXT).

## Lessons

- DNS is a favourite exfiltration channel because it is rarely blocked.
- A prefix with file name and part number gives the reassembly away.
- RC4 with a weak key protects nothing: it is obfuscation.
