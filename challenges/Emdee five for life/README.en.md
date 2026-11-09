---
challenge: Emdee five for life
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, md5, automation, python]
---

# Emdee five for life — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

The page generates a random string and asks for its **MD5**. Doing it by hand is too slow: the string expires and the response changes. The challenge is automation: one HTTP session, pull the string with a regex, hash it, post the result in under a second. Once the loop is fast enough, the response carries the flag.

## Prompt

```text
Encrypt this string into md5 and send it back.
String: 6Ml1m0JmWq
```

A single-field form named `hash`.

## Analysis

- Every `GET /` issues a new string and stores it in the session (`PHPSESSID` cookie).
- `POST /` compares the submitted `hash` against the MD5 of the string issued for **that** session.
- Sending the hash of an old string, or reusing the session without re-reading it, returns `Too slow!`.

This is a timing exercise, not cryptography: MD5 is not broken here, it is computed.

## Exploitation

```python
import re, hashlib, requests

s = requests.Session()
r = s.get("http://<IP>:<PORT>/")
cadena = re.search(r"<h3 align='center'>([A-Fa-f0-9]+)</h3>", r.text).group(1)
# if the HTML changes, anchor on the tag wrapping the random text
digest = hashlib.md5(cadena.encode()).hexdigest()
r = s.post("http://<IP>:<PORT>/", data={"hash": digest})
print(r.text)
```

```text
HTB{<flag>}
```

Burp works too: `Ctrl+R` the request, `Send to Repeater`, and drive it with a pre-request script or an Intruder payload. The script is the clean path.

## Pitfalls

- **Loose regex**: capturing the wrong `<h3>` (there are several) and hashing decorative text.
- **New session per request**: `requests.get` without `Session` drops the cookie, so the string never matches.
- **Uppercase MD5**: the server compares lowercase; `hexdigest()` already returns that.

## Lessons

- A timing-based "anti-bot" control breaks against an HTTP client; it adds friction, not security.
- Automating the whole cycle (read, transform, submit, keep state) is the skill the challenge trains.
- Real mitigation: per-account rate limits, CAPTCHA and session verification, not a one-second timer.
