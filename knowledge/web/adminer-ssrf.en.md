---
topic: Adminer — SSRF in the Elasticsearch login (CVE-2021-21311)
tags: [web, adminer, ssrf, elasticsearch, pivot]
---

# Adminer — SSRF in the Elasticsearch login (CVE-2021-21311)

**English** | [🌐 Español](adminer-ssrf.md)

## Concept

Adminer 4.7.8 lets the Elasticsearch login server field make a request from the server. An attacker hosts an endpoint that returns a `301` to an internal destination; Adminer follows the redirect and returns the result. This is an SSRF useful for discovering and attacking loopback-only services.

## When it applies

- Adminer is exposed and the Elasticsearch login is available.
- The server can reach the attacker host and follow redirects.
- Internal services such as databases, panels or APIs are not visible externally.

## Procedure

1. Confirm the Adminer version and the Elasticsearch driver.
2. Run an attacker server that returns `301 Location: http://127.0.0.1:<PORT>/...`.
3. Put the attacker IP in the server field and submit the login.
4. Read the response and repeat across ports and paths to enumerate the interior.

## Commands

```bash
python3 -m http.server 80
# In another terminal, return a 301 to the internal target
curl -i "http://<HOST>/adminer.php?server=<ATTACKER>&username=x&password=x&auth[driver]=elastic"
curl -s "http://127.0.0.1:4242/api/version"
```

## Variants

- Redirect to `gopher://` to send a complete HTTP request to a service that does not speak HTTP.
- Point `Location` at a port range to build an internal scanner.
- Use a wildcard DNS name to bypass IP-based filters.

## Limitations

- Adminer must reach the attacker; an egress firewall blocks it.
- Some drivers do not follow redirects or restrict the scheme.
- The SSRF returns the response, but not always methods other than GET.

## Mitigation

- Update Adminer and disable unused drivers.
- Restrict server egress and block loopback access from web components.
- Require authentication and segment administration services.

## Detection

- Outbound requests from the web server to unusual hosts.
- `301` responses followed by connections to `127.0.0.1` in the same flow.
- Adminer requests with `server` values that are not known databases.

## References

- [0xdf — AdmirerToo](https://0xdf.gitlab.io/2022/05/28/htb-admirertoo.html)
- [NVD — CVE-2021-21311](https://nvd.nist.gov/vuln/detail/CVE-2021-21311)
- [CWE-918 — Server-Side Request Forgery](https://cwe.mitre.org/data/definitions/918.html)
