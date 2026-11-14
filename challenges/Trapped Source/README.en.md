---
challenge: Trapped Source
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, client-side, source-code, pin, information-disclosure]
---

# Trapped Source — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The page asks for a PIN, but the client-side JavaScript contains the expected value in clear text. No server-side check protects the secret: open the source, read the PIN and submit it.

## Statement and surface

- Web, Very Easy, retired.
- A URL with a PIN form is provided.
- The goal is to reach the screen that displays the flag.

```bash
curl -s http://<IP>:<PORT>/ | head -n 40
```

## Reconnaissance

- The response is static HTML with a form and a script.
- There are no relevant headers or additional routes.
- The field accepts four digits and validates in the browser.

```bash
curl -s http://<IP>:<PORT>/ | grep -iE 'pin|script|input'
```

## Code analysis

The script compares the input with a constant. The comparison and the value are included in the bundle, so anyone can read them with the inspector or `curl`.

```javascript
const expected = "<PIN>";
if (value === expected) { showFlag(); }
```

There is no server call validating the PIN before revealing the content; the protection is purely visual.

## Why it works

The application treats a client-side secret as a security boundary. The browser must know the value to compare it, so the value is accessible. The check can be skipped by changing local state or by submitting the correct PIN.

## Local reproduction

```bash
# Save the page and open it in a local browser.
curl -s http://<IP>:<PORT>/ -o trapped.html
```

- Open `trapped.html` and view the source.
- Find the PIN constant.
- Enter it in the form.

## Exploitation

1. View the source with `Ctrl-U` or `curl`.
2. Locate the constant compared with the input.
3. Submit the PIN.
4. The page displays the flag; it is redacted.

```bash
curl -s http://<IP>:<PORT>/ | grep -oE '[0-9]{4}' | head
```

## Evidence

- Screenshot of the source with the PIN redacted.
- Submitted form and success screen.
- Redacted flag.

## Lessons learned

- A client-side secret is not a secret.
- Validation must happen on the server and the secret must not be sent to the browser.
- Source code is part of the attack surface.

## Mitigations and detection

- Validate the PIN server-side with rate limiting and lockout.
- Do not include the expected value or the flag in the bundle.
- Serve the flag only after an authenticated and authorized session.
- Alert on repeated attempts and bulk HTML downloads.

## References

- <https://www.hackthebox.com/challenges/Trapped%20Source>
- <https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure>
- <https://attack.mitre.org/techniques/T1213/>
