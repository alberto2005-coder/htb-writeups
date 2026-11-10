---
challenge: Keep Tryin'
type: Forensics
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [forensics, pcap, dns-exfil, base64url, rc4]
---

# Keep Tryin' — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A **26-packet** PCAP with two `POST`s and **DNS TXT** queries. The first subdomain decodes to `secret.txt|1`: file name and part number, i.e. DNS exfiltration. The parts are concatenated, decrypted with **RC4** using the key from `POST /flag`, and yield a ZIP with `secret.txt`.

## Brief

`keeptrying.zip` (password `hackthebox`) → `keeptryin.pcap`. Nothing else: no server, no binary; the traffic is the evidence.

## Recon

```bash
tshark -r keeptryin.pcap | head -40
tshark -r keeptryin.pcap -Y 'http.request.method=="POST"' -T fields -e http.request.uri -e http.file_data
tshark -r keeptryin.pcap -Y 'dns.qry.type==16' -T fields -e dns.qry.name
```

## The flaw

Two loose pieces that only make sense together:

- `POST /flag` sends the string **`TryHarder`**: it looks like noise, but it is the symmetric key.
- `POST /lootz` sends `S2VlcCB0cnlpbmcsIGJ1ZmZ5Cg==`, decoding to *"Keep trying, buffy"*: a hint, not data.
- The TXT queries go to `<part>.totallylegit[.]com`, with the file chunk as subdomain.

```text
init.c2VjcmV0LnR4dHwx.totallylegit.com
```

`c2VjcmV0LnR4dHwx` does not decode with standard base64 because it uses the **base64url** alphabet (`-` and `_`). With the right alphabet it reads `secret.txt|1`.

## Exploitation

1. **Collect and sort**: take the subdomains, drop `init` and the domain, and sort by the index after `|`.
2. **Concatenate** the decoded chunks in order.
3. **Decrypt**: the result is not text (`file` says `data`); RC4 with the key `TryHarder` reveals the `PK` magic bytes.

```text
From Base64 (url safe) → RC4 (key: TryHarder) → Unzip
```

4. **Open** the ZIP: `secret.txt` holds the flag.

## Evidence

- Trimmed `tshark` output; no flags or keys published.
- Real values live in `private/`.

## Lessons

- **base64 vs base64url**: the alphabet changes and the wrong one fails.
- **Part order**: without the subdomain index the ZIP comes out corrupt.
- **`file` before guessing**: `data` means encrypted; `PK` proves the inverse is right.
- **Apparent noise**: `POST /flag` was the key; discarding "what makes no sense" costs the challenge.

- DNS is a common exfiltration channel because it is rarely blocked.
- A prefix carrying file name and part number gives the reconstruction away.
- RC4 with a weak key protects nothing: it is obfuscation.
- Mitigation: alert on long, high-entropy TXT queries and block unauthorised resolvers.
