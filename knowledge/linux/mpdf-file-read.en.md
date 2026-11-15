---
topic: mPDF — file read from templates
tags: [linux, mpdf, file-read, pdf, lfi]
---

# mPDF — file read from templates

**English** | [🌐 Español](mpdf-file-read.md)

## Concept

mPDF generates PDFs from HTML and can include local resources. If an application passes a user-controlled path into a template, image or `@import`, the library resolves `file://` and relative paths. The result is server file read, including configuration with credentials.

## When it applies

- The application generates PDFs with mPDF and accepts templates or paths.
- The parameter is not restricted to a directory.
- Credentials or source code are sought.

## Procedure

1. Identify the PDF generation endpoint.
2. Try absolute paths and `file://` in the parameter.
3. Read configuration, `.env` or SSH keys.
4. Reuse the credentials over SSH or another service.

## Commands

```bash
curl -s "http://<HOST>/pdf.php?template=../../../../etc/passwd"
curl -s "http://<HOST>/pdf.php?template=file:///var/www/.env"
curl -s -o out.pdf "http://<HOST>/report?html=file:///etc/passwd"
```

## Variants

- Inject `file://` into an `img` or `link` tag.
- Use CSS `@import` to read files.
- Chain it with SSRF to reach internal services.

## Limitations

- mPDF may block `file://` in recent versions.
- The file must be readable by the service user.
- Output may be inside the PDF and need extraction.

## Mitigation

- Restrict templates to a directory and an allowlist.
- Disable `file://` and remote resources.
- Run the generator as a user without secret access.

## Detection

- Template parameters with `../` or `file://`.
- PDFs containing `/etc/passwd` or `.env`.
- File reads from the PHP process.

## References

- [mPDF — Documentation](https://mpdf.github.io/)
- [0xdf — Faculty](https://0xdf.gitlab.io/2022/10/22/htb-faculty.html)
- [CWE-22 — Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
