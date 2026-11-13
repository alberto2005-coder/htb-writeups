---
topic: Python path join upload
tags: [linux, python, flask, upload, path-traversal, secure-filename]
---

# Python path join upload

**English** | [🇪🇸 Español](python-path-join-upload.md)

## Concept

`os.path.join(base, user_value)` discards `base` when `user_value` is absolute. If a Flask or Django application uses the client-supplied filename without `secure_filename`, the attacker can write anywhere the process may write, not just inside the upload directory.

## When it applies

- XML, image, CSV or document upload forms.
- Applications that save a file before validating it.
- Errors that reveal the saved path.
- Script or cron directories writable by the web service.

## Requirements and conditions

- Control of the multipart `filename` field.
- Write permission for the web process at the destination.
- Knowledge of a useful path, such as a scripts directory.
- No canonicalisation or prefix check.

## Procedure

1. Identify the upload parameter and base directory.
2. Send a `filename` containing an absolute path.
3. Confirm the write through an error, response or download.
4. Find a consumer of that path: cron, import, template or task.
5. Execute code on the consumer's next cycle.

```python
files = {
    "xml_file": ("/var/www/app/scripts/task.py", open("payload.py", "rb")),
    "xslt_file": ("stub.xslt", open("stub.xslt", "rb")),
}
requests.post("http://<HOST>/convert", files=files, cookies=cookies)
```

## Variants

- Absolute `filename`.
- `../` sequences when the framework does not normalise them.
- Symlinks inside the upload directory.
- Writing into a directory present in `PYTHONPATH`.

## Limitations

- The process must be able to write to the destination.
- Some frameworks normalise or reject absolute paths.
- The path may be outside the web server's reach.
- The file must be consumed by a useful process.

## Mitigation

- Use `werkzeug.utils.secure_filename`.
- Resolve the path and verify it starts with the allowed directory.
- Store with a generated name and validated extension.
- Do not execute scripts from directories writable by the web service.

## Detection

- Alert on filenames containing `/`, `..` or absolute paths.
- Monitor writes to script directories.
- Review parser errors that mention unexpected paths.
- Audit cron and processes importing files from upload directories.

## References

- <https://docs.python.org/3/library/os.path.html#os.path.join>
- <https://werkzeug.palletsprojects.com/en/stable/utils/#werkzeug.utils.secure_filename>
- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
- <https://attack.mitre.org/techniques/T1059/006/>
