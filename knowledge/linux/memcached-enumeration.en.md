---
topic: Memcached — unauthenticated enumeration
tags: [linux, memcached, enumeration, cache, credentials]
---

# Memcached — unauthenticated enumeration

[🌐 Español](memcached-enumeration.md) | **English**

## Concept

Memcached listens on 11211 without authentication by default. When exposed, `stats`, `stats items` and `lru_crawler metadump all` list keys and recover cached sessions, tokens or credentials.

## When it applies

- Port 11211 reachable directly or through SSRF/proxy.
- Applications caching sessions or query results.
- Legacy instances without SASL or a firewall.

## Procedure

1. Confirm the service with `nc` and `stats`.
2. List slabs and keys with `stats items`.
3. Dump keys with `lru_crawler metadump all`.
4. Inspect values for sessions or credentials.
5. Reuse the data against the application.

## Commands

```bash
printf 'stats\r\n' | nc -nv <HOST> 11211
printf 'stats items\r\n' | nc -nv <HOST> 11211
printf 'lru_crawler metadump all\r\n' | nc -nv <HOST> 11211
```

## Variants

- UDP/11211 for amplification or enumeration.
- PHP or Rails session keys.
- Cached database credentials.

## Limitations

- The service may require SASL.
- Keys may have expired.
- A firewall may restrict the source.

## Mitigation

- Listen only on `127.0.0.1`.
- Filter 11211 and enable SASL.
- Do not cache secrets in clear text.

## Detection

- External connections to 11211 and `stats`/`metadump` commands.
- Cache traffic spikes from unusual hosts.

## References

- <https://memcached.org/>
- <https://attack.mitre.org/techniques/T1552/>
