---
topic: Flask upload with an absolute path
tags: [web, flask, upload, path-join, rce]
---

# Flask upload with an absolute path

[🌐 Español](flask-absolute-path-upload.md) | **English**

## Concept

`os.path.join` discards earlier components when a later one is absolute. If an application blocks `../` but passes the filename to `os.path.join`, a name such as `/app/app/views.py` writes outside the upload directory.

## When it applies

- The application allows file uploads.
- The name is passed to `os.path.join`.
- Application code is writable or reloads.

## Procedure

1. Download the source if available.
2. Identify a view or file loaded at startup.
3. Upload a file with an absolute name.
4. Request the route to run the code.

```python
import os
os.path.join('/app', 'public', 'uploads', '/app/app/views.py')
# '/app/app/views.py'
```

```http
POST /upcloud HTTP/1.1
Content-Disposition: form-data; name="file"; filename="/app/app/views.py"
```

## Variants

- Overwrite a template or configuration file.
- Use a leading slash with an allowed extension.
- Combine with Flask debug to run code.

## Limitations

- The process must be able to write the destination.
- The file must load or reload.
- The absolute path must be accepted.

## Mitigation and detection

- Use `secure_filename` and confine the path.
- Reject absolute names and normalize.
- Mount code read-only.

## References

- <https://docs.python.org/3/library/os.path.html#os.path.join>
- <https://flask.palletsprojects.com/en/stable/patterns/fileuploads/>
- <https://attack.mitre.org/techniques/T1190/>
