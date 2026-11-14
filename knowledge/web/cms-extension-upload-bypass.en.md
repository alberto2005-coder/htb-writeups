---
topic: CMS upload blacklist bypass
tags: [web, cms, upload, blacklist, php]
---

# CMS upload blacklist bypass

[🌐 Español](cms-extension-upload-bypass.md) | **English**

## Concept

A CMS blocks `.php`, `.phtml` and similar extensions but forgets variants the server still treats as PHP (`.php5`, `.php7`, `.phar`). A blacklist does not cover Apache's real handler map.

## When it applies

- Media managers with extension blacklists.
- Apache with `AddHandler`/`SetHandler` for PHP.
- Publicly served upload directories.

## Procedure

1. Identify the CMS and version.
2. Enumerate blocked and allowed extensions.
3. Try an alternative extension with a harmless PHP file.
4. Check the public path and execution.

```bash
printf '<?php echo 7*7; ?>' > test.php5
curl -s -F "file=@test.php5" http://<HOST>/upload
curl -s http://<HOST>/uploads/test.php5
```

## Variants

- `.pht`, `.phtm`, `.phar`, `.inc`.
- Double extension `file.php.jpg` with loose config.
- Uppercase or trailing dot on Windows.
- `.htaccess` mapping an extension.

## Limitations

- The server must interpret the extension.
- The upload path must be reachable.
- Content filters may block the payload.

## Mitigation and detection

- Use allowlists and rename files.
- Serve uploads from a non-executable domain.
- Disable PHP handlers in user directories.
- Alert on uploads with uncommon PHP extensions.

## References

- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://www.exploit-db.com/exploits/41936>
- <https://attack.mitre.org/techniques/T1505/003/>
