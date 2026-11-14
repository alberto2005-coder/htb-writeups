---
machine: Knife
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, php, backdoor, chef, sudo]
---

# Knife — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site advertises PHP 8.1.0-dev, the version with the `User-Agentt` backdoor. Sending the malicious header yields a shell as `james`; `sudo knife` runs Ruby as root and completes the box.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
curl -s http://<IP>/ | head
```

## Enumeration

- The response includes `X-Powered-By: PHP/8.1.0-dev`.
- There are no relevant routes or forms; the site is a single page.
- `james` can run `/usr/bin/knife` with passwordless sudo.

## Initial access

Version 8.1.0-dev contains a backdoor that evaluates `User-Agentt` when it starts with `zerodium`. Send a `system` call carrying a reverse shell and obtain execution as `james`.

## Privilege escalation

`sudo -l` shows `(root) NOPASSWD: /usr/bin/knife`. Knife is the Chef CLI and its `exec` subcommand evaluates Ruby; `sudo knife exec -E "exec '/bin/bash'"` opens a root shell. Alternatively, `knife data bag create` opens Vim and `:!/bin/bash` escapes.

## Evidence

- `X-Powered-By` header showing 8.1.0-dev.
- `User-Agentt` request and shell as `james`.
- `sudo knife exec` and `id` as root.

## Lessons learned

- An exact service version can be a vulnerability by itself.
- Automation CLIs with `exec` are equivalent to full sudo.
- Checking `sudo -l` remains a priority.

## Mitigation and detection

- Do not run development builds in production.
- Restrict `knife` and remove `exec` from sudo rules.
- Monitor anomalous HTTP headers and PHP child processes.

## References

- [0xdf — Knife](https://0xdf.gitlab.io/2021/08/28/htb-knife.html)
- [IppSec — Knife](https://www.youtube.com/watch?v=93JnRTF5sQM)
- [Hack The Box — Knife](https://app.hackthebox.com/machines/knife)
