---
topic: JPEG — attacker-controlled metadata and XXE in the pipeline
tags: [web, xxe, jpeg, exiftool, metadata, file-read]
---

# JPEG — attacker-controlled metadata and XXE in the pipeline

[🌐 Español](jpeg-metadata-xxe.md) | **English**

## Concept

An application reads a JPEG's `Artist` field and uses it to build the path of a credit XML. If the attacker controls the image and the log that points to it, they can redirect the path to their own XML. That XML declares an external entity that reads a server file; the process, running as root, writes the content into the response.

## When it applies

- The application processes metadata from uploaded or reachable images.
- The metadata value is concatenated into a file path.
- The resulting XML is parsed with external entities enabled.
- The process has high privileges.

## Procedure

1. Identify the metadata field used in the path.
2. Create a JPEG with `exiftool -Artist=...` pointing at the XML.
3. Create the XML with `<!ENTITY xxe SYSTEM "file:///...">`.
4. Make the application process the image (upload, log or cron).
5. Read the result wherever the application stores the field.

## Commands

```bash
exiftool -Artist="../tmp/x" x.jpg
```

```xml
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///root/.ssh/id_rsa">]>
<credits><image><root>&xxe;</root></image></credits>
```

## Variants

- Use `exiftool` with `-Comment` or `-ImageDescription`.
- Target `/etc/passwd` to confirm the read.
- Chain with a writable log to control the path.
- Read SSH keys and use them to log in.

## Limitations

- The parser must resolve external entities.
- The built path must be reachable by the process.
- The file must be processed after upload.
- The result must be readable.

## Mitigation

- Disable external entities (`resolve_entities=False`).
- Never build paths from user metadata.
- Validate `Artist` against an allowlist.
- Run the processing as an unprivileged user.

## Detection

- JPEGs whose `Artist` contains `../` or absolute paths.
- XML with `DOCTYPE` and `ENTITY SYSTEM`.
- SSH key reads by image-processing processes.
- Parser errors while processing credits.

## References

- [OWASP — XXE](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing)
- [ExifTool — Documentation](https://exiftool.org/)
- [0xdf — RedPanda](https://0xdf.gitlab.io/2022/11/26/htb-redpanda.html)
