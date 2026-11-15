---
topic: Nginx off-by-slash
tags: [web, nginx, alias, proxy-pass, traversal]
---

# Nginx off-by-slash

[🌐 Español](nginx-off-by-slash.md) | **English**

## Concept

A `location /admin` rule using `alias` or `proxy_pass` without a trailing slash can interpret `/admin../path` as a jump to the parent directory. This reaches applications or files outside the intended prefix.

## When it applies

- Nginx uses `alias` or `proxy_pass` without a trailing slash.
- A protected or unlinked path exists.
- The backend trusts the rewritten path.

## Procedure

1. Try `/admin..` and `/admin../`.
2. Look for `index.php` or a known route.
3. Adjust the number of segments.
4. Access the internal panel or file.

```bash
curl -i 'http://<IP>/admin../admin_staging/index.php'
curl -i 'http://<IP>/admin../admin_staging/'
```

## Variants

- Apply the same trick to static `alias` rules.
- Combine with LFI to read configuration.
- Use slash encodings.

## Limitations

- The rule must be malformed.
- The backend must accept the resulting path.
- Nginx may normalize the URI.

## Mitigation and detection

- Add trailing slashes and use `location =` or `^~`.
- Normalize the URI before rewriting.
- Audit proxy and alias configurations.

## References

- <https://nginx.org/en/docs/http/ngx_http_core_module.html#alias>
- <https://i.blackhat.com/us-18/Wed-August-8/us-18-Orange-Tsai-Breaking-Parser-Logic-Take-Your-Path-Normalization-Off-And-Pop-0days-Out-2.pdf>
- <https://attack.mitre.org/techniques/T1190/>
