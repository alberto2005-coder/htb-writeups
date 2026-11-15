---
title: WordPress — webshell hidden in a theme
tags: [web, wordpress, php, webshell, theme, persistence]
---

# WordPress — webshell hidden in a theme

[🇪🇸 Español](wordpress-theme-webshell.md) | **English**

## Concept

A WordPress theme can contain a malicious PHP file that only answers a specific parameter. Being inside `wp-content/themes`, the server executes it and traffic blends with legitimate assets. It is common persistence after a compromise.

## When it applies

- The active theme has files that do not match upstream.
- `wpscan` enumerates the theme and versions.
- There is an odd parameter in requests or obfuscated code.

## Procedure

1. Enumerate themes and compare with the official repository.
2. Look for `eval`, `base64_decode`, `gzinflate` and `$_REQUEST` variables.
3. Deobfuscate the file and find the parameter and key.
4. Invoke the webshell with the correct parameter.

```bash
wpscan --url http://<IP> --enumerate t,tt
curl 'http://<IP>/wp-content/themes/<THEME>/<FILE>.php?<PARAM>=id'
```

## Variants

- The webshell may be in `functions.php` behind an `init` hook.
- A plugin or mu-plugin also provides persistence.
- The key may be in a cookie or header.

## Limitations

- The file must be reachable over HTTP.
- The parameter and key must be found by analysis.
- WAFs may block command execution.

## Mitigation and detection

- Verify integrity with `wp core verify-checksums` and compare themes.
- Audit new files and modification dates.
- Apply least privilege to the web user.
- Monitor requests to theme PHP files with system parameters.

## References

- <https://developer.wordpress.org/themes/basics/theme-functions/>
- <https://wpscan.com/>
- <https://wordpress.org/documentation/article/hardening-wordpress/>
