---
topic: File upload
tags: [web, file-upload, webshell, mime, magic-bytes, bypass]
---

# File upload

**English** | [🇪🇸 Español](file-upload.md)

## Concept

An insecure upload lets an attacker store an executable file or read it from a controlled path. Defences often rely on extension, MIME type or content; each can fail independently when the server trusts the client or does not normalise the filename.

## When it applies

- Avatar, document or import forms.
- Extension or MIME filters.
- An upload directory served by the webroot.
- Later processing with a vulnerable library.

## Procedure

1. Identify allowed extension, MIME and size.
2. Test extension variants and casing.
3. Manipulate `Content-Type` and magic bytes.
4. Check whether the file is served or executed.
5. Look for an execution or read path.

```bash
curl -F 'file=@sh.php;type=image/png' http://<HOST>/upload
curl -F 'file=@sh.phtml' http://<HOST>/upload
curl -F 'file=@shell.jpg' http://<HOST>/upload
```

## Variants

- Bypass with `.php5`, `.phtml`, `.phar` or a double extension.
- A polyglot with an image header and PHP code.
- `.htaccess` to interpret another extension.
- Path traversal in the filename.

## Limitations

- The directory must be reachable or executable.
- The server may rename the file.
- Validation may inspect magic bytes.
- Antivirus may remove the payload.

## Mitigation and detection

- Validate real content and allowed extension.
- Generate random names and store outside the webroot.
- Disable execution in the upload directory.
- Alert on executable extensions and mixed-header files.

## References

- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://attack.mitre.org/techniques/T1505/003/>
- <https://portswigger.net/web-security/file-upload>
