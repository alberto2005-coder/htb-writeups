---
sherlock: Bumblebee
domain: DFIR
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, phpbb, sqlite, access-log, web-shell, credential-theft]
---

# Bumblebee — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; platform answers are not reproduced.

## Scenario

An external contractor joined the company's internal forum over the guest Wi-Fi and apparently walked away with an administrator's credentials. Only two artefacts exist: the forum's SQLite database (phpBB) and the web server's `access.log`.

## Evidence

```text
incident.tgz
├── phpbb.sqlite3
└── access.log
```

## Investigation

### 1. Database inventory

```bash
sqlite3 phpbb.sqlite3 ".tables"
sqlite3 phpbb.sqlite3 ".schema phpbb_users"
```

Relevant tables: `phpbb_users`, `phpbb_posts`, `phpbb_topics`, `phpbb_log`, `phpbb_sessions`. Sort users by registration date to find the contractor's account and note its registration IP (`user_ip`).

```bash
sqlite3 -header -column phpbb.sqlite3 \
  "SELECT user_id, username, user_ip, user_regdate FROM phpbb_users ORDER BY user_regdate;"
```

### 2. The malicious post

Review the suspect user's messages looking for HTML/JS or an external link:

```bash
sqlite3 phpbb.sqlite3 "SELECT post_id, poster_id, post_time, post_text FROM phpbb_posts WHERE poster_id=<id>;"
```

The pattern is a post with an image or link carrying credentials in the URL, or a fake form: when the administrator opens it, their browser sends username and password to the attacker's server.

### 3. Correlate with the access log

```bash
grep '<contractor_ip>' access.log | head
grep -i 'POST /ucp.php' access.log | head
```

Look for `POST` requests to `ucp.php?mode=login` from the contractor IP after the post, plus a `200` with a valid session. Also requests to `download/file.php` or the admin panel (`adm/index.php`) to confirm privilege escalation.

### 4. Escalation and exfiltration

With admin access, the attacker promoted their own account (or created one), then exported the database:

```bash
grep -E 'adm/index.php.*(mode=.*user|action=.*)' access.log
grep -i 'backup\|\.sql\|\.sqlite' access.log
```

Login `POST`, group change and backup download together close the chain.

## Findings

- Entry: account created over guest Wi-Fi with no email verification.
- Movement: post delivering credential phishing aimed at the administrator.
- Result: admin account takeover, self-promotion and database export.
- MITRE: T1566 (phishing), T1078 (valid accounts), T1005/T1567 (collection and exfiltration).

## Lessons

- A forum with open registration and no link moderation is an internal phishing platform.
- The `access.log` is what turns "an odd post" into a timeline: IP, time, endpoint and status code.
- In phpBB, watch group changes (`phpbb_user_group`) and backup downloads; a legitimate admin does not do those daily.
