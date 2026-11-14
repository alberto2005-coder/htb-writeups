---
topic: Client-side source disclosure
tags: [web, javascript, source-maps, secrets, information-disclosure]
---

# Client-side source disclosure

**English** | [🇪🇸 Español](client-side-source-disclosure.md)

## Concept

The browser must execute JavaScript, so code and embedded data are accessible. Comments, unminified bundles, source maps, configuration variables and validation constants can reveal routes, keys, PINs or internal logic.

## When it applies

- SPAs with large bundles.
- Reachable `.map` files.
- HTML comments with credentials or routes.
- PIN, coupon or role checks in JavaScript.
- `API_KEY`, `SECRET` or internal endpoint variables.

## Procedure

1. View source and the Network tab.
2. Look for `.js`, `.map` and `chunk` files.
3. Review comments and strings with `grep`.
4. Format the bundle with `prettier` or browser tooling.
5. Test discovered routes and values.

```bash
curl -s https://<HOST>/ | grep -oE 'src="[^"]+\.js[^"]*"'
curl -s https://<HOST>/static/app.js | grep -iE 'api|secret|token|pin|admin'
```

## Variants

- Source map reconstructing the source tree.
- API secret in the bundle.
- PIN or discount validation logic.
- Hidden admin route.
- Comment with test credentials.

## Limitations

- A client secret protects nothing, but may be read-only.
- Source maps may be disabled in production.
- Obfuscated bundles slow reading but do not prevent it.
- Domain-restricted keys reduce impact.

## Mitigation and detection

- Keep secrets and authorization logic out of the client.
- Disable source maps in production or restrict them.
- Validate everything on the server.
- Alert on `.map` downloads and access to discovered routes.

## References

- <https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure>
- <https://cwe.mitre.org/data/definitions/540.html>
- <https://attack.mitre.org/techniques/T1213/>
- <https://developer.chrome.com/docs/devtools/javascript/source-maps/>
