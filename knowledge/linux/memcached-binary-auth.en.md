---
topic: Memcached — SASL authentication over the binary protocol
tags: [linux, memcached, sasl, binary-protocol, dyplesher]
---

# Memcached — SASL authentication over the binary protocol

[🌐 Español](memcached-binary-auth.md) | **English**

## Concept

Memcached has no authentication in its classic configuration. When started with `-S` and built with SASL, it requires authentication, but only over the binary protocol: ASCII tools (`memcached-tool`, `nc`) stop working. Credentials usually appear in application configs, systemd units or environment variables.

## When it applies

- Memcached reachable on `11211`.
- A banner or `stats` that only answers the binary protocol.
- Processes or configuration files with a SASL username and password.
- On Dyplesher, the credentials were in the application config and allowed dumping keys.

## Procedure

1. Confirm the port and SASL mode.
2. Get credentials from the application, systemd or environment.
3. Connect with a client that supports binary + SASL.
4. List slabs and keys, then dump the values.
5. Reuse any secrets found.

## Commands

```bash
nmap -sV -p11211 <IP>
printf 'version\r\n' | nc -nv <IP> 11211
```

With `pymemcache`:

```python
from pymemcache.client.base import Client

c = Client(('<IP>', 11211), binary=True,
           sasl_username='<USER>', sasl_password='<PASSWORD>')
print(c.stats())
for key in c.stats('items'):
    print(key)
```

`memcached-tool` cannot authenticate; to dump keys:

```bash
memcdump --servers=<IP> --binary --username=<USER> --password=<PASSWORD>
memccat --servers=<IP> --binary --username=<USER> --password=<PASSWORD> <KEY>
```

## Variants

- `stats items` and `stats cachedump <slab> <limit>` to enumerate keys when ASCII is allowed.
- `lru_crawler metadump all` on recent versions.
- SASL credentials in `/etc/memcached.conf`, `systemd` or the app `.env`.
- Reuse the password against SSH, a database or the application panel.

## Limitations

- Without `-S`, SASL is not used and the binary does not authenticate.
- Some clients only speak ASCII.
- The port may be on loopback or behind a firewall.
- Keys may have expired.

## Mitigation

- Do not expose memcached to the Internet; bind to loopback or an internal network.
- Enable SASL with strong credentials and TLS where possible.
- Rotate credentials and never reuse them.
- Restrict `11211` by firewall and monitor access.

## Detection

- Connections to `11211` from unexpected hosts.
- `stats items`, `get` or `lru_crawler` commands in traffic.
- Processes reading memcached configuration.
- SASL credentials used from new IPs.

## References

- [Memcached — SASL](https://github.com/memcached/memcached/wiki/SASLHowto)
- [Memcached — Binary protocol](https://github.com/memcached/memcached/wiki/BinaryProtocolRevamped)
- [0xdf — Dyplesher](https://0xdf.gitlab.io/2020/10/03/htb-dyplesher.html)
- [Dyplesher writeup](../../machines/linux/dyplesher/README.en.md)
