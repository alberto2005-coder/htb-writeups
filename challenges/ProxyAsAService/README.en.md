---
challenge: ProxyAsAService
type: Web
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [web, ssrf, localhost-bypass, http]
---

# ProxyAsAService — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A web proxy fetches URLs and blocks `localhost`/`127.0.0.1` with a blacklist. Alternate IP representations and redirects reach the internal service and read the flag.

## Prompt and surface

- Web, Medium, retired.
- Form accepting a URL.
- Filter blocking local destinations.

```bash
curl 'http://<HOST>/?url=http://example.com'
```

## Reconnaissance

Confirm the backend makes the request. Try internal destinations and observe the block message.

```bash
curl 'http://<HOST>/?url=http://127.0.0.1:80'
```

## Analysis

1. Try alternate representations: `127.1`, `0.0.0.0`, `[::1]`, decimal, octal.
2. Use your own domain that redirects to `localhost`.
3. Reach the internal port.
4. Read the flag path.
5. Document the bypass.

```bash
curl 'http://<HOST>/?url=http://127.1:<PORT>/'
curl 'http://<HOST>/?url=http://<ATTACKER>/redirect'
```

## Root cause

Defence relies on a string blacklist, not on resolving and validating the final IP. Redirects and alternate formats bypass the filter.

## Local reproduction

1. Run a proxy with a blacklist.
2. Expose an internal service.
3. Try variants.
4. Add an allowlist/IP validation.
5. Compare.

## Evidence

- Blocked request.
- Bypass and internal response.
- Redacted flag.

## Lessons learned

- `localhost` blacklists are bypassable.
- Resolve DNS before connecting.
- Redirects can bypass filters.
- SSRF affects internal services.

## Mitigation and detection

- Allowlist destinations.
- Resolve and validate the final IP.
- Block private ranges and metadata.
- Do not follow redirects automatically.

## References

- <https://www.hackthebox.com/challenges/proxyasaservice>
- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://github.com/swisskyrepo/PayloadsAllTheThings>
