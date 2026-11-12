---
challenge: Mutation Lab
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, svg, file-read, session-forgery, flask]
---

# Mutation Lab — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The app processes uploaded SVG and reads local files through external references. With the leaked session secret, an admin cookie is forged and the flag obtained.

## Prompt and surface

- Web, Easy, retired.
- SVG upload/processing.
- Cookie-based session.

```bash
curl -i http://<HOST>/
```

## Reconnaissance

Review the code and confirm the SVG is rendered server-side. Try a reference to `file:///etc/passwd` or an internal path.

```xml
<svg xmlns="http://www.w3.org/2000/svg">
  <image href="file:///etc/passwd"/>
</svg>
```

## Analysis

1. Upload the SVG and see if content is reflected.
2. Read the app configuration file.
3. Extract `SECRET_KEY`.
4. Forge an admin session cookie.
5. Access the panel and read the flag.

```python
from flask.sessions import SecureCookieSessionInterface
# sign {'user':'admin'} with the leaked SECRET_KEY
```

## Root cause

The SVG renderer allows external references and the session key is in a readable file. The app trusts a cookie signed with a leaked secret.

## Local reproduction

1. Run the Flask app.
2. Upload the SVG.
3. Read the configuration.
4. Forge the cookie.
5. Access the panel.

## Evidence

- Malicious SVG.
- Read file and redacted secret.
- Forged cookie and redacted flag.

## Lessons learned

- SVG can reference external resources.
- Session secrets must not be readable by the app.
- A signed cookie is not safe if the key leaks.
- Rendering user files is dangerous.

## Mitigation and detection

- Disable external references in SVG.
- Rotate `SECRET_KEY` and use a secret manager.
- Validate and sanitise SVG.
- Monitor access to configuration files.

## References

- <https://www.hackthebox.com/challenges/mutation-lab>
- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://flask.palletsprojects.com/en/stable/quickstart/#sessions>
