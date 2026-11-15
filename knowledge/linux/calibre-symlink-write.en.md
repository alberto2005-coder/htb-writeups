---
topic: Calibre — arbitrary write through symlinks
tags: [linux, calibre, symlink, file-write, privesc]
---

# Calibre — arbitrary write through symlinks

**English** | [🌐 Español](calibre-symlink-write.md)

## Concept

An ebook conversion service using Calibre often runs as its owner. If it accepts controlled files or paths and follows symlinks, conversion can write outside the working directory and modify files such as `.ssh/authorized_keys`.

## When it applies

- An internal Calibre converter is reachable from another user.
- The service writes into the target user's directory.
- Symlinks are neither resolved nor blocked.

## Procedure

1. Find the port and process owner (`ps`, `ss`).
2. Create an ebook-named symlink to the target file.
3. Upload it and trigger conversion.
4. Verify the write and log in with the key.

## Commands

```bash
ln -s /home/neil/.ssh/authorized_keys book.epub
# upload book.epub and convert to PDF/EPUB
ssh -i id_ed25519 neil@bookworm.htb
```

## Variants

- Symlink in the output directory or cover path.
- Metadata referencing absolute paths.
- Batch conversion with controlled names.

## Limitations

- The service may run as a user without a home or `.ssh`.
- A `realpath` or `O_NOFOLLOW` blocks the attack.
- Read-only containers prevent writes.

## Mitigation

- Resolve paths and reject symlinks.
- Run the converter as a user without `.ssh` access.
- Mount the workdir with `noexec,nosuid` and minimal permissions.

## Detection

- Unexpected symlinks in uploads or output directories.
- Writes to `.ssh` from a conversion process.
- Off-hours `ebook-convert` CPU spikes.

## References

- [0xdf — Bookworm](https://0xdf.gitlab.io/2024/01/20/htb-bookworm.html)
- [Calibre — ebook-convert](https://manual.calibre-ebook.com/generated/en/ebook-convert.html)
- [CWE-59 — Link Following](https://cwe.mitre.org/data/definitions/59.html)
