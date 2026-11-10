---
sherlock: NeuroSync-D
domain: DFIR / Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [dfir, nextjs, cve-2025-29927, ssrf, lfi, redis, bci]
---

# NeuroSync-D — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; no platform answers.

## Scenario

NeuroSync builds BCI (brain-computer interface) devices and its site runs on **Next.js**. An APT group is inside and moving laterally; some online devices were hijacked through an *N-day*. Emulate the offensive chain, then explain it from the logs.

## Evidence

```text
NeuroSync/
├── interface.log      (Next.js stdout: startup plus one line per request)
├── access.log         (frontend)
├── data-api.log       (internal API)
├── redis.log          (job queue)
└── bci-device.log     (hardware communication)
```

## Investigation

### 1. Version and CVE

`interface.log` opens with the Next.js banner (`Local: http://localhost:3000`) and records the `User-Agent` and status of every request. The version predates the **CVE-2025-29927** fix: an authorization bypass in the middleware achieved by sending the repeated internal header.

```bash
grep -h "Local:" interface.log
grep -i "x-middleware-subrequest" interface.log | head
# x-middleware-subrequest: middleware:middleware:middleware:middleware:middleware
```

### 2. Web recon

`access.log` first shows requests to the usual Next.js static files to fingerprint the build (`main-app.js`, `_buildManifest.js`) returning `200`, and then the vulnerable endpoint with the bypass header.

### 3. SSRF and the internal API

With the middleware skipped, the attacker makes the server fetch internal addresses and discovers an **API on port 4000**. `data-api.log` keeps the scan and the follow-up requests.

### 4. LFI and secrets

The API exposes a log-reading endpoint vulnerable to path traversal: first `/etc/passwd`, then its own source and a **secret** file (`secrets.txt`). With the signing key the attacker can forge messages the queue accepts.

### 5. RCE through Redis injection

The app consumes jobs from **Redis**. The attacker publishes a signed command that, once decoded, downloads and executes against an external host; `bci-device.log` and `redis.log` record the effect on the device.

## Findings

- Entry: **CVE-2025-29927** in the Next.js middleware.
- Recon: SSRF to map the internal network and find the API on 4000.
- Data: LFI on the log endpoint up to the source and the signing secret.
- Impact: Redis queue injection → execution on the BCI device.

## Lessons

- A middleware bypass needs no exotic payload: the repeated internal header is enough.
- Application (`interface.log`) and API (`data-api.log`) logs must be correlated: each sees half.
- A secret on the web server is a key to any service that signs with it.
- Mitigation: patch Next.js (>= 15.2.3 / 14.2.25 / 13.5.9 / 12.3.5), strip internal headers at the edge, keep APIs off flat networks and authenticate Redis.
