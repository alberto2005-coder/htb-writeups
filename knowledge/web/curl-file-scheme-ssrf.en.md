---
topic: SSRF — curl with multiple URLs and file://
tags: [web, ssrf, curl, file-scheme, filter-bypass]
---

# SSRF — curl with multiple URLs and file://

**English** | [🌐 Español](curl-file-scheme-ssrf.md)

## Concept

An SSRF calling `curl` may accept more than one URL in the same argument. Even if `file://` is blocked on the first, a second URL with that scheme can read local files and reveal code or secrets.

## When it applies

- Input is passed directly to `curl`.
- The filter only inspects the first URL or searches strings.
- The server allows local schemes.

## Procedure

1. Confirm the URL is controllable.
2. Send two space-separated URLs.
3. Use `file:///etc/passwd` or source.
4. Read the response and escalate.

## Commands

```bash
url=http://<ATTACKER>/&url=file:///var/www/html/index.php
# or: url=http://<ATTACKER>/ file:///etc/passwd
```

## Variants

- `file://` with encoding or uppercase.
- `gopher://` to interact with services.
- Redirects to local schemes.

## Limitations

- Modern `curl` may restrict protocols.
- The filter may validate every URL.
- The process may use `--proto -file`.

## Mitigation

- Validate URL and scheme with an allowlist.
- Use `--proto =http,https` and resolve once.
- Do not let users control arguments.

## Detection

- Requests with `file://`, `gopher://` or multiple URLs.
- Local file reads from the web service.
- Connections to internal destinations.

## References

- [0xdf — Down](https://0xdf.gitlab.io/2025/06/17/htb-down.html)
- [curl — URL syntax](https://curl.se/docs/url-syntax.html)
- [PortSwigger — SSRF](https://portswigger.net/web-security/ssrf)
