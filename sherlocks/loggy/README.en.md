---
sherlock: Loggy
domain: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, logs, web-server, access-log, triage]
---

# Loggy — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

A web server keeps alerting on odd requests. Application and system logs are provided; the job is to identify the malicious activity, the targeted resource, and whether it succeeded.

## Evidence

- `access.log` and `error.log`.
- Authentication logs for the same period.
- Server configuration (vhosts, paths).

## Investigation

### 1. Normalise the format

```bash
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head
awk '{print $7}' access.log | sort | uniq -c | sort -rn | head -20
```

Top IPs and paths separate scanner noise from the real attacker: few, highly targeted requests with a tool `User-Agent`.

### 2. Find the attack pattern

```bash
grep -Ei "union|select|\.\./|/etc/passwd|cmd=|shell|\.env" access.log | head -30
```

Classify what you find: traversal, injection, upload, path scanning. Status codes say whether it worked: a `200` where a `403` belongs is the signal.

### 3. Close the window

```bash
grep "<ATTACKER_IP>" access.log | awk '{print $4, $6, $7, $9}' | head -40
```

The full ordered sequence (recon → exploit → resource access) is the answer. Check for later requests from the same IP against other vhosts.

## Findings

- Targeted activity against a specific web resource.
- The line between attempt and compromise lives in status codes and response size.
- Automated scanners in the rest of the log are background noise.

## Lessons

- `awk` plus `sort | uniq -c` solves half a log case before opening anything else.
- Comparing response size (`$10`) exposes data extraction that a bare `200` hides.
- A log without synchronised clocks cannot be correlated: NTP is forensic too.
