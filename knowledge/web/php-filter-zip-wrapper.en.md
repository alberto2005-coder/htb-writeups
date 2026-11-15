---
topic: PHP — LFI with php://filter and zip://
tags: [web, php, lfi, php-filter, zip-wrapper, rce]
---

# PHP — LFI with php://filter and zip://

**English** | [🌐 Español](php-filter-zip-wrapper.md)

## Concept

An LFI that appends `.php` can read code with `php://filter` and execute an uploaded file with `zip://` or `phar://`. The combination turns file inclusion into source disclosure and RCE.

## When it applies

- A parameter reaches `include`/`require`.
- A ZIP or PHAR can be uploaded.
- Wrappers are not disabled.

## Procedure

1. Confirm the LFI and appended suffix.
2. Read code with `php://filter/convert.base64-encode`.
3. Upload a ZIP containing PHP.
4. Include it with `zip://` and run a command.

## Commands

```bash
curl -s 'http://<HOST>/?op=php://filter/convert.base64-encode/resource=home' | base64 -d
curl -s 'http://<HOST>/?op=zip://uploads/<IP>/<FILE>.zip%23shell.php&cmd=id'
```

## Variants

- `phar://` for deserialization.
- `data://` when `allow_url_include` is on.
- `expect://` on old installs.

## Limitations

- `allow_url_include=Off` does not block `zip://`.
- The `.php` suffix must fit the ZIP name.
- The upload directory must be reachable by relative path.

## Mitigation

- Use an allowlist and absolute paths.
- Disable unnecessary wrappers.
- Store uploads outside the webroot and rename them.

## Detection

- Requests with `php://`, `zip://`, `phar://` or base64 in parameters.
- Upload access followed by PHP execution.
- Inclusion errors with encoded paths.

## References

- [PHP — wrappers](https://www.php.net/manual/en/wrappers.php)
- [0xdf — CrimeStoppers](https://0xdf.gitlab.io/2018/06/03/htb-crimestoppers.html)
- [HackTricks — LFI](https://book.hacktricks.wiki/en/pentesting-web/file-inclusion/index.html)
