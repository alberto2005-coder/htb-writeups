---
topic: SSRF con oráculo HMAC
tags: [web, ssrf, hmac, proxy, internal-network]
---

# SSRF con oráculo HMAC

**English** | [🇪🇸 Español](hmac-oracle-ssrf.md)

## Concept

The application signs internal requests with HMAC but exposes an endpoint that signs arbitrary parameters. Combined with SSRF, the attacker builds valid requests to internal services that would otherwise reject the signature.

## When it applies

- SSRF with URL validation but no real destination restriction.
- Signing endpoint accepting user data.
- Internal services trusting an HMAC header.

## Procedure

1. Identify the signed parameter and HMAC format.
2. Use the oracle to sign a custom request.
3. Send the request through the SSRF.
4. Repeat to enumerate internal routes and actions.

```bash
curl 'http://<HOST>/sign?data=GET%20/internal%20HTTP/1.1'
curl 'http://<HOST>/proxy?url=http://internal/&sig=<HMAC>'
# Local proxy that signs and forwards
python3 ssrf_hmac_proxy.py --target http://<HOST> --listen 8000
```

## Variants

- Separate signing of body, path or method.
- HMAC with a user-derived key.
- Blind SSRF with callback and timing.
- Redirects changing the destination after signing.

## Limitations

- The oracle must sign the exact expected format.
- The SSRF must allow the internal destination.
- The key may include non-controllable context.

## Mitigation and detection

- Do not expose a signing oracle; sign only predefined operations.
- Validate destinations, resolve DNS and block internal ranges.
- Use mTLS and per-service authorization, not HMAC alone.

## References

- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://portswigger.net/web-security/ssrf>
- <https://attack.mitre.org/techniques/T1190/>
