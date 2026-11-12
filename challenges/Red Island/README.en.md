---
challenge: Red Island
type: Web
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [web, ssrf, gopher, redis, rce]
---

# Red Island — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

An SSRF reaches internal Redis through `gopher://`. Keys/cron or a module are written to execute commands and read the flag.

## Prompt and surface

- Web, Medium, retired.
- Parameter accepting a URL.
- Internal Redis without authentication.

```bash
curl 'http://<HOST>/?url=http://example.com'
```

## Reconnaissance

Confirm SSRF with a listener. Scan internal ports and identify Redis (6379).

```bash
curl 'http://<HOST>/?url=http://127.0.0.1:6379'
```

## Analysis

1. Build a `gopher://` payload with RESP commands.
2. Use `redis-cli` or a script to generate the stream.
3. Write a cron or malicious module.
4. Execute the command.
5. Read the flag.

```bash
python3 gopherus.py --exploit redis
```

## Root cause

SSRF allows arbitrary protocols and Redis has no authentication. `gopher` carries RESP commands, turning SSRF into RCE.

## Local reproduction

1. Run Redis and an SSRF proxy.
2. Confirm access.
3. Send `PING` over gopher.
4. Write a cron.
5. Verify execution.

## Evidence

- Confirmed SSRF.
- Redis response.
- Executed command and redacted flag.

## Lessons learned

- `gopher` extends SSRF to TCP protocols.
- Redis without auth is RCE.
- System cron is a target.
- Scheme filtering is essential.

## Mitigation and detection

- Allowlist schemes and destinations.
- Redis auth and local bind.
- Block `gopher`/`dict`/`file`.
- Monitor Redis commands and cron.

## References

- <https://www.hackthebox.com/challenges/red-island>
- <https://github.com/tarunkant/Gopherus>
- <https://redis.io/docs/management/security/>
