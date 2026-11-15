---
topic: Request smuggling h2c
tags: [web, http2, h2c, smuggling, proxy]
---

# Request smuggling h2c

**English** | [🇪🇸 Español](http2-request-smuggling.md)

## Concept

A proxy accepts cleartext HTTP/2 (h2c) and forwards the request to the backend without normalizing the protocol. The attacker embeds an HTTP/1.1 request inside the h2c stream to reach routes blocked by the frontend.

## When it applies

- Frontend enforcing path rules and a backend accepting h2c.
- Proxy/cache chains that convert protocols.
- `Upgrade: h2c` or `HTTP2-Settings` accepted without validation.

## Procedure

1. Check whether the server accepts h2c with `curl --http2-prior-knowledge`.
2. Request a blocked route and compare status codes.
3. Build the smuggling request with `h2cSmuggler` or a raw request.
4. Confirm the backend processes the internal route.

```bash
curl --http2-prior-knowledge -sv http://<HOST>/admin
python3 h2cSmuggler.py -u http://<HOST>/admin
# Raw request with Upgrade: h2c and HTTP2-Settings
```

## Variants

- HTTP/2 to HTTP/1.1 conversion at the proxy.
- CL.TE/TE.CL smuggling combined with h2c.
- Internal routes protected only by the frontend.
- Cache poisoning with the internal response.

## Limitations

- The backend must accept h2c or the proxy must forward it.
- Proxy rules may normalize the headers.
- The internal route must exist and be sensitive.

## Mitigation and detection

- Reject h2c at the edge and use HTTP/2 only over TLS.
- Normalize protocol and headers on every hop.
- Enforce authorization in the backend, not only at the proxy.

## References

- <https://portswigger.net/web-security/request-smuggling>
- <https://www.rfc-editor.org/rfc/rfc9113>
- <https://attack.mitre.org/techniques/T1190/>
