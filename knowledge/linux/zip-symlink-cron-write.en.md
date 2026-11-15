---
topic: Cron — predictable symlink and arbitrary write
tags: [linux, cron, symlink, arbitrary-write, privesc]
---

# Cron — predictable symlink and arbitrary write

**English** | [🌐 Español](zip-symlink-cron-write.md)

## Concept

A root process that builds filenames with `rand()` or a predictable timestamp and follows symlinks can redirect writes to a sensitive file, such as `/root/.ssh/authorized_keys`.

## When it applies

- The cron runs at a known second or pattern.
- The filename is computed with a predictable PRNG.
- The output directory is attacker-writable.

## Procedure

1. Observe the exact cron time.
2. Reproduce the filename calculation.
3. Create a symlink to the target file.
4. Insert the content into the database or input.

## Commands

```bash
ln -s /root/.ssh/authorized_keys /var/local/<HASH>
# insert the public key into the table read by the cron
# wait for the run and log in over SSH
```

## Variants

- Write to `/etc/cron.d` or a backup script.
- Names based on `date` or a counter.
- Race between check and write.

## Limitations

- The name may include strong random bytes.
- The directory may have `fs.protected_symlinks`.
- The process may use `O_NOFOLLOW`.

## Mitigation

- Use `mkstemp` and `O_NOFOLLOW`.
- Do not run backups as root.
- Write to directories users cannot control.

## Detection

- Symlinks in `/var/local` or backup directories.
- New keys in `authorized_keys`.
- Cron runs writing outside their directory.

## References

- [0xdf — CrossFit](https://0xdf.gitlab.io/2021/03/20/htb-crossfit.html)
- [CWE-59 — Link Following](https://cwe.mitre.org/data/definitions/59.html)
- [Linux — protected_symlinks](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/fs.html)
