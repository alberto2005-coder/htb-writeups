---
challenge: Baby nginxatsu
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, nginx, alias-traversal, configuration]
---

# Baby nginxatsu — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

A misconfigured nginx `alias` allows escaping the intended directory and reading files outside the webroot. The flag is at a path reachable through traversal.

## Prompt and surface

- Web, Easy, retired.
- A URL served by nginx is provided.
- No initial credentials.

```bash
curl -i http://<HOST>/
```

## Reconnaissance

Review routes and identify `alias` locations. Test traversal with and without encoding:

```bash
curl --path-as-is 'http://<HOST>/assets/../../../../etc/passwd'
```

## Analysis

1. Confirm the nginx version and exposed configuration.
2. Identify `location /assets/ { alias /var/www/assets/; }`.
3. A missing trailing `/` in `alias` allows `../` concatenation.
4. Encode `../` if a proxy normalizes.
5. Read the flag path.

```bash
curl --path-as-is 'http://<HOST>/assets../flag.txt'
```

## Root cause

An `alias` without a trailing slash and without normalization resolves outside the directory. It is a configuration flaw, not nginx itself.

## Local reproduction

1. Configure nginx with a bad `alias`.
2. Create a file outside the webroot.
3. Test traversal.
4. Fix the `alias` and compare.
5. Redact the flag.

## Evidence

- Configuration/version.
- Traversal request.
- Read file and redacted flag.

## Lessons learned

- `alias` and `root` behave differently.
- The trailing slash changes resolution.
- Proxies may or may not normalize.
- Configuration is attack surface.

## Mitigation and detection

- Prefer `root` where possible.
- Add a trailing `/` and normalize paths.
- Block `..` and validate the resolved path.
- Alert on traversal in logs.

## References

- <https://www.hackthebox.com/challenges/baby-nginxatsu>
- <https://nginx.org/en/docs/http/ngx_http_core_module.html#alias>
- <https://owasp.org/www-community/attacks/Path_Traversal>
