---
topic: PHP — filter injection and conversion chains
tags: [web, php, lfi, php-filter, file-read, rce]
---

# PHP — filter injection and conversion chains

[🇪🇸 Español](php-filter-injection.md) | **English**

## Concept

An LFI that allows `php://filter` can turn a file read into code writing. Conversion chains (`convert.iconv`, `convert.base64-decode`) transform controlled data into valid PHP that is included and executed.

## When it applies

- A parameter reaches `include`, `require` or `file_get_contents`.
- The `php://` scheme is not blocked.
- The attacker controls part of the read content (an uploaded file or a session, for example).

## Procedure

1. Confirm the LFI and that `php://filter` works.
2. Build a chain with `php_filter_chain_generator`.
3. Write a webshell or run code in the response.
4. With `php-fpm`, combine it with a poisoned session.

```bash
python3 php_filter_chain_generator.py --chain '<?php system($_GET["c"]); ?>'
```

## Variants

- `convert.base64-decode` to clean characters.
- Long chains to bypass length limits.
- Poison a session and use it as the source.

## Limitations

- `allow_url_include` must be on for some flows.
- The chain may exceed the URL length limit.
- `open_basedir` restricts accessible files.

## Mitigation

- Do not allow `php://` in include parameters.
- Use file allowlists and absolute paths.
- Disable `allow_url_include` and isolate sessions.

## Detection

- Parameters with `php://filter` or `convert.iconv`.
- Abnormally long URLs.
- Includes from `uploads/` or sessions.

## References

- [Synacktiv — PHP filter chains](https://www.synacktiv.com/publications/php-filter-chains-file-read-from-error-based-oracle)
- [0xdf — Pollution](https://0xdf.gitlab.io/2023/07/01/htb-pollution.html)
- [PHP — wrappers](https://www.php.net/manual/en/wrappers.php.php)
