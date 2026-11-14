---
topic: SSRF y lectura de archivos con PDFKit
tags: [web, ruby, pdfkit, ssrf, file-read, cve-2022-25765]
---

# PDFKit SSRF and File Read

**English** | [🇪🇸 Español](pdfkit-ssrf.md)

## Concept

PDFKit converts HTML or a URL to PDF with `wkhtmltopdf`. If the user chooses the URL and it is unrestricted, the server can request internal resources or read files with `file://`. Old versions also allow option injection.

## When it applies

- Forms that generate a PDF from a URL.
- `PDFKit.new(params[:url])` without a host allowlist.
- Metadata revealing `pdfkit`/`wkhtmltopdf`.

## Procedure

1. Generate a PDF from your own URL and inspect metadata.
2. Try `http://127.0.0.1` and internal ports.
3. Try `file:///etc/passwd`.
4. Review the version and accepted options.
5. Confirm impact without publishing sensitive data.

```bash
curl -s 'http://<IP>/' --data-urlencode 'url=file:///etc/passwd'
```

## Variants

- Option injection in `wkhtmltopdf`.
- SSRF to cloud metadata (`169.254.169.254`).
- Reading keys and configuration.

## Limitations

- A host/scheme allowlist blocks the attack.
- The service may run without network.
- Process permissions limit reads.

## Mitigation

- Allow only `https` and known hosts.
- Block private IPs and metadata.
- Update PDFKit and never concatenate options.
- Run the converter in a sandbox without secrets.

## Detection

- Requests to `127.0.0.1`, `file://` and `169.254.169.254`.
- PDFs generated from internal hosts.
- `wkhtmltopdf` errors.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2022-25765>
- <https://owasp.org/www-community/attacks/Server_Side_Request_Forgery>
- <https://attack.mitre.org/techniques/T1190/>
