---
machine: Health
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, laravel, ssrf, gogs, sqlite, sqli, cron]
---

# Health — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Laravel application redirects to a monitoring URL and is vulnerable to SSRF. The internal Gogs service leaks the user table through an SQLite SQLi; the cracked hash provides SSH. A cron that reads the database executes tasks and allows a command to be written as root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,3000 <IP>
```

- SSH, HTTP and an internal service.
- The site is a health platform with forms and redirects.
- Gogs is reachable from localhost.

## Enumeration

- A monitoring route accepts a URL and returns a redirect.
- The parameter reaches `http://127.0.0.1:3000` and Gogs.
- The Gogs version has an SQLi in user search.
- The SQLite database contains users and hashes.

## Foothold

Use the redirect/SSRF to query Gogs. Exploit the SQLi with a union and extract a user hash. Crack it outside the platform and log in over SSH.

```bash
curl -s 'http://health.htb/monitor' --data-urlencode 'url=http://127.0.0.1:3000'
sqlmap -r gogs.req --dbms=sqlite
```

## Privilege escalation

A cron reads a database task and passes the result to a command. Insert a task with a controlled payload; when it runs as root, obtain a shell or copy a SUID binary.

```bash
pspy64
sqlite3 <DB> '.tables'
```

## Evidence

- SSRF against Gogs.
- Extracted hash and SSH session.
- Task table and cron execution.
- Root through the injected task.

## Lessons

- Internal redirects can bypass SSRF filtering.
- An old Gogs adds SQLi to the chain.
- Crons consuming user data are a privilege-escalation path.
- The SQLite database is both a read and write target.

## Mitigations and detection

- Validate destinations and do not follow internal redirects.
- Update Gogs and use parameterised queries.
- Never run user tasks as root.
- Alert on database queries from cron and task changes.
- References: CVE-2022-30781, OWASP SSRF, HTB Health.

## References

- <https://www.hackthebox.com/machines/Health>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-30781>
- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://attack.mitre.org/techniques/T1053/003/>
