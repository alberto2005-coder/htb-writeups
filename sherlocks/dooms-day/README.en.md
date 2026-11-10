---
sherlock: dOOMs Day
domain: SOC
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, web, php, php2shell, cve-2026-109618, cve-2026-109619, log-analysis]
---

# dOOMs Day — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

An Apache server running **PHP 8.4.26** keeps recycling workers and has a child process that should not exist. `access.log`, `error.log` and a capture are provided; rebuild the **PHP2Shell** exploitation (CVE-2026-109618 / CVE-2026-109619), which never touches the application: it lives in PHP's multipart parser.

## Evidence

- Apache `logs/access.log` and `logs/error.log`.
- `capture.pcap` for the period.

## Investigation

### 1. Worker exhaustion

```bash
grep AH00161 "logs/error.log" | wc -l
```

Apache reports that no children are available dozens of times from a single client: the attacker keeps multipart uploads stalled until the whole prefork pool is busy (149 of 150 by default).

### 2. An OOM that is not a crash

```bash
grep -m1 "Allowed memory size" "logs/error.log"
```

The default limit (`128M` = `134217728` bytes) is crossed on purpose. When ZendMM cannot allocate it does not return `NULL`: it calls `zend_bailout` (`longjmp`), skips the request teardown and leaves session pointers dangling. The worker survives and reuses that dirty state on the next request: the use-after-free primitive.

### 3. The two CVEs

- **CVE-2026-109618**: memory-exhaustion corruption while parsing, before the script runs.
- **CVE-2026-109619**: stale global state outliving the request memory.

Fixed in PHP **8.4.27** (and 8.2.35 / 8.3.36 / 8.5.12). The field that triggers both is `PHP_SESSION_UPLOAD_PROGRESS`, handled in `main/rfc1867.c` before the application: that is why `access.log` says almost nothing and `error.log` says everything.

### 4. ASLR leak through the response

The dangling session is reclaimed with a forged header and PHP writes ~600 KB of neighbouring heap into `Set-Cookie: PHPSESSID=...`; from there come the `libphp.so` and chunk bases. Access-log signal: `Set-Cookie` headers hundreds of KB long.

```bash
awk '{print length($0)}' logs/access.log | sort -rn | head
```

### 5. Post-exploitation

With the bases known, a forged `zend_array` whose `pDestructor` points at `zif_system` yields execution as `www-data`. The PCAP shows the reverse shell to **4444**; on the host, child processes of the worker (`sh -c ...`), not of the final binary.

## Findings

Unauthenticated compromise without touching the application: the vector is the PHP runtime (`session.upload_progress`) and the evidence is in `error.log` (worker exhaustion plus OOM), not in the web logs.

## Lessons

- A memory fatal is not a crash: it is a `longjmp` that can leave reusable state behind.
- Exploitation happens **before** the script: it works even on a page with no PHP.
- `error.log` is the primary artifact; `access.log` only gives the client and the sizes.

## Detection and mitigation

- `session.upload_progress.enabled = Off` when progress bars are unused: one line, nothing breaks.
- Update to PHP 8.4.27+ (8.2.35 / 8.3.36 / 8.5.12).
- Realistic `memory_limit` and a `MaxRequestWorkers` sized to the container.
- Alerts: repeated `AH00161` from one client, `Allowed memory size` followed by a worker child, `Set-Cookie` hundreds of KB long, `PHP_SESSION_UPLOAD_PROGRESS` in a request body.
