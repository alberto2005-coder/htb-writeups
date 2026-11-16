---
machine: Heal
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, rails, lfi, limesurvey, consul, privesc]
---

# Heal — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site uses three domains: main, API and survey. The API has a directory traversal in `/download` that reads Rails configuration and SQLite databases; crack the admin hash and reuse it on LimeSurvey. A PHP plugin gives a webshell as `www-data`; the PostgreSQL password is reused for `ron`, and an unauthenticated localhost Consul allows registering a service whose check runs as root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH and `80` nginx with a resume generation site.
- Vhosts `heal.htb`, `api.heal.htb` and `take-survey.heal.htb`.
- The API issues JWTs and the survey site is LimeSurvey 6.6.4.

## Enumeration

Register an account and get a JWT. `/download?filename=` returns files without path normalization; use `../../` to read `config/database.yml`, `storage/development.sqlite3` and `test.sqlite3`. The users table contains `ralph`'s bcrypt hash, which cracks and works on LimeSurvey.

## Foothold

LimeSurvey allows uploading plugins as ZIP. Create a plugin with a function that runs commands and activate it from the UI; calling it gives a webshell as `www-data`. LimeSurvey's configuration contains the PostgreSQL password, try it against system users and it works for `ron`.

```bash
# traversal
curl --path-as-is -H 'Authorization: Bearer <JWT>' \
  'http://api.heal.htb/download?filename=../../storage/development.sqlite3' -o dev.sqlite3
# Consul
curl -X PUT http://127.0.0.1:8500/v1/agent/service/register -d @svc.json
/tmp/root -p
```

## Lateral movement

`ron` logs in over SSH. `ps` shows a Consul agent running as root and listening on `127.0.0.1:8500`.

## Privilege escalation

Consul has no ACLs. Register a service with a `Check` whose `args` copy bash to `/tmp` and set SUID; the agent runs the check periodically as root. Then run the copy with `-p`.

## Evidence

- Traversal in `/download`.
- SQLite databases and `ralph` hash.
- LimeSurvey plugin and `www-data` shell.
- PostgreSQL password reused by `ron`.
- Consul service with a root check.

## Lessons learned

- A download endpoint must resolve and confine the path.
- Application hashes may be reused on another service.
- CMS plugins are executable code.
- Consul without ACLs on localhost is still a root path.

## Mitigation and detection

- Normalize and allowlist paths.
- Do not reuse passwords across services.
- Sign and review plugins; restrict uploads.
- Enable Consul ACLs and avoid root checks.

## References

- [0xdf — Heal](https://0xdf.gitlab.io/2025/05/17/htb-heal.html)
- [IppSec — Heal](https://www.youtube.com/watch?v=7KsIks7bdp8)
- [Hack The Box — Heal](https://app.hackthebox.com/machines/heal)
