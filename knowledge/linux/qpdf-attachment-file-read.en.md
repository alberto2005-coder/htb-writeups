---
topic: qpdf — reading privileged files with attachments
tags: [linux, qpdf, pdf, sudo, file-read, privesc]
---

# qpdf — reading privileged files with attachments

[🌐 Español](qpdf-attachment-file-read.md) | **English**

## Concept

`qpdf` can create an empty PDF and attach files with `--add-attachment`. If the binary runs under sudo, the file is read with root privileges and stored inside the PDF. The attacker only needs to extract the attachment afterwards. This is not a qpdf vulnerability: it is a legitimate feature delegated badly.

## When it applies

- `sudo -l` allows `/usr/bin/qpdf` as any user; it may prompt for the user's password.
- The user can read the resulting PDF.
- Sensitive files are readable by root.

## Procedure

1. Confirm the sudo rule and version.
2. Create an empty PDF with `--empty`.
3. Add the target file with `--add-attachment`.
4. Terminate attachment options with `--` before the output name.
5. Extract or open the attachment.

## Commands

```bash
sudo qpdf --empty --add-attachment /root/.ssh/id_rsa -- out.pdf
qpdf --show-attachment=id_rsa out.pdf
qpdf --list-attachments out.pdf
```

## Variants

- Attach `/etc/shadow` or `/root/root.txt`.
- Use `--replace-input` to overwrite an existing PDF.
- Chain with `scp` to exfiltrate the PDF.
- Add several files in one run.

## Limitations

- qpdf needs `--` to end the attachment options.
- The file must exist and be readable by root.
- The resulting PDF must be readable or copyable.
- Some sudo rules restrict allowed arguments.

## Mitigation

- Do not delegate unrestricted qpdf to non-administrators.
- Use a sudo rule with a wrapper and an allowlist.
- Restrict access to root keys and files.
- Audit generated PDFs and their attachments.

## Detection

- `qpdf --add-attachment` in UID 0 processes.
- PDFs created in `/tmp` or `/dev/shm` by regular users.
- `/root/.ssh` reads by qpdf processes.
- Sudo rules allowing generic binaries.

## References

- [qpdf — Manual](https://qpdf.readthedocs.io/)
- [qpdf — Embedded files](https://qpdf.readthedocs.io/en/stable/cli.html#embedded-files)
- [0xdf — IClean](https://0xdf.gitlab.io/2024/08/03/htb-iclean.html)
