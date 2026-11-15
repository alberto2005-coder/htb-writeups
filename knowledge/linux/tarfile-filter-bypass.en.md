---
topic: Python tarfile — data filter bypass
tags: [linux, python, tarfile, cve-2025-4517, symlink, arbitrary-write]
---

# Python tarfile — data filter bypass

**English** | [🌐 Español](tarfile-filter-bypass.md)

## Concept

`tarfile`'s `data` filter tries to prevent writes outside the extraction directory, but CVE-2025-4517 bypasses it with crafted paths and symlinks. If the script runs as root, it can write to `/root/.ssh/authorized_keys`.

## When it applies

- A root script extracts a controlled tar.
- It uses `tarfile.extractall(filter='data')` on a vulnerable version.
- The destination is outside the attacker's view.

## Procedure

1. Check the Python version and filter.
2. Create a tar with a symlink and escaping path.
3. Run the restore as root.
4. Check the written key.

## Commands

```bash
python3 -c 'import tarfile; print(tarfile.__file__)'
# build a tar with a symlink to /root/.ssh/authorized_keys and run the script
```

## Variants

- Paths with `..` or absolute links.
- `filter='tar'` may also be unsafe.
- Write to `/etc/cron.d` or a service.

## Limitations

- Patched Python rejects the tar.
- The script may validate the manifest.
- The destination may be read-only.

## Mitigation

- Update Python to a fixed version.
- Validate members and resolve symlinks.
- Extract as an unprivileged user.

## Detection

- Tars with symlinks or absolute paths.
- Writes to `/root` from a restore.
- Off-hours restore runs.

## References

- [0xdf — WingData](https://0xdf.gitlab.io/2026/06/27/htb-wingdata.html)
- [NVD — CVE-2025-4517](https://nvd.nist.gov/vuln/detail/CVE-2025-4517)
- [Python — tarfile filters](https://docs.python.org/3/library/tarfile.html#extraction-filters)
