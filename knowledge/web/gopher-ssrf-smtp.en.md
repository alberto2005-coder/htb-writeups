---
topic: Gopher SSRF — internal email over SMTP
tags: [web, ssrf, gopher, smtp, phishing]
---

# Gopher SSRF — internal email over SMTP

[🇪🇸 Español](gopher-ssrf-smtp.md) | **English**

## Concept

A proxy that only blocks `GET` may accept `POST` with a `url` parameter. If it allows the `gopher` scheme, every byte of the URL becomes a TCP connection; with `%0d%0a` it can speak SMTP, Redis, internal HTTP or any text protocol. This sends mail from `localhost` without authentication and bypasses external exposure.

## When it applies

- A proxy or webhook validates the method but not the scheme.
- The internal service trusts connections from `127.0.0.1`.
- SMTP listens on localhost and accepts mail without authentication.

## Procedure

1. Confirm `POST` reaches the backend and `url` is controllable.
2. Try `gopher://127.0.0.1:25/` and observe the response.
3. Build the SMTP sequence with double-encoded CRLFs.
4. Send mail with a malicious link or attachment.

```text
gopher://127.0.0.1:25/_HELO%20localhost%250d%250aMAIL%20FROM%3A%3Cattacker%40local%3E%250d%250aRCPT%20TO%3A%3Cvictim%40local%3E%250d%250aDATA%250d%250aSubject%3A%20test%250d%250a%250d%250ahello%250d%250a.%250d%250aQUIT%250d%250a
```

## Variants

- `gopher://` against Redis to write a file or a module.
- `dict://` for plain-text services.
- A 302 redirect to `gopher://` when only the first URL is validated.

## Limitations

- The gopher scheme must be allowed.
- The proxy may normalize or block CRLF.
- The SMTP server may require TLS or authentication.

## Mitigation

- Allowlist schemes and destinations; block private and loopback IPs.
- Resolve and validate the IP after every redirect.
- Require SMTP authentication and restrict local relay.

## Detection

- Proxy requests to `127.0.0.1`, `[::1]` or private ranges.
- Unauthenticated SMTP connections from the web server.
- URLs containing `%250d%250a` or `gopher://` in logs.

## References

- [0xdf — Gofer](https://0xdf.gitlab.io/2023/10/28/htb-gofer.html)
- [curl — gopher protocol](https://curl.se/docs/manpage.html#gopher)
- [CWE-918 — Server-Side Request Forgery](https://cwe.mitre.org/data/definitions/918.html)
