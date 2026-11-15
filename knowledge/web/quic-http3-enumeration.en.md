---
title: QUIC/HTTP3 — enumerating a service that does not speak HTTP/1.1
tags: [web, quic, http3, curl, enumeration, udp]
---

# QUIC/HTTP3 — enumerating a service that does not speak HTTP/1.1

[🇪🇸 Español](quic-http3-enumeration.md) | **English**

## Concept

QUIC carries HTTP/3 over UDP and does not answer a normal `curl`. A service can look closed on TCP while listening on UDP/9001 or UDP/443. Enumerating it needs an HTTP/3 client and often the correct vhost.

## When it applies

- `nmap` TCP does not show the web app, but a UDP scan finds the port.
- `curl https://host:port` fails with a connection or protocol error.
- The certificate or banner mentions HTTP/3 or QUIC.

## Procedure

1. Scan UDP and confirm the port.
2. Use a `curl` built with HTTP3 (`curl -V` must include `HTTP3`).
3. Force HTTP/3 with `--http3-only`.
4. Add the vhost to `/etc/hosts` if the certificate requires it.

```bash
nmap -Pn -sU -p9001 <IP>
curl -V | grep -i http3
curl --http3-only -k https://quick.htb:9001/
```

## Variants

- `nghttp3`/`ngtcp2` or `quiche` for low-level tests.
- `openssl s_client -quic` on recent versions.
- If the server falls back, `--http3` may be enough.

## Limitations

- Many distro `curl` builds lack HTTP3.
- Some firewalls block UDP.
- The vhost and SNI must match the certificate.

## Mitigation and detection

- Inventory UDP services and do not assume TCP only.
- Apply the same authentication and WAF rules to HTTP/3.
- Monitor anomalous QUIC traffic and UDP scans.
- Keep the server updated and limit protocols.

## References

- <https://curl.se/docs/http3.html>
- <https://www.rfc-editor.org/rfc/rfc9114.html>
- <https://blog.cloudflare.com/the-quic-approach-to-connection-migration/>
