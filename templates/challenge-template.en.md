---
challenge: Name
category: Challenge
type: web
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
solved: YYYY-MM-DD
points: 0
tags: [web, php, pwn]
---

# Name — Hack The Box (Challenge)

**English** | [🇪🇸 Español](challenge-template.md)

> **State:** Retired / Active (private draft).
> Real flags live in `private/` and are never published.

## TL;DR

What the challenge is, where the bug lives and what it gets you, in 3–5 lines.

## Brief and surface

- Category and difficulty.
- What ships with the challenge (source, binary, container, URL).
- Clues in the description.

## Recon

```bash
curl -s -I http://<IP>:<port>/
```

- Headers and technologies.
- Exact versions (the ones that pin offsets or the CVE).
- What is absent (endpoints, parameters, forms).

## Source analysis

- Relevant files and default configuration.
- The vulnerable line or function.
- Why the bug is reachable unauthenticated.

## The bug

Explain the mechanism (memory corruption, crypto, logic...) in enough detail to reproduce it. ASCII diagrams when they help.

## Local reproduction

```bash
# build/run the container or binary
```

- How to debug it (gdb, breakpoints, symbols).
- Build-specific offsets or constants and how to obtain them.

## Exploitation

```bash
python3 exploit.py --url http://<IP>:<port>/
```

- The chain, step by step.
- Output that proves execution.
- Limits (payload size, ASLR, workers, outbound network).

## Evidence

- Trimmed output, no flags or tokens.

## Lessons learned

- What was tried and failed.
- Script or environment mistakes.
- What you would do differently.

## Mitigations and detection

- Fixed version or safe configuration.
- Detection rules (WAF, logs, upload limits).
- References (CVE, MITRE ATT&CK).

## References

- ...
