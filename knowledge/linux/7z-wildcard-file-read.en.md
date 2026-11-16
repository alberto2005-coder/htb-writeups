---
topic: 7-Zip — wildcard and @lists for file reads
tags: [linux, 7z, wildcard, listfile, file-read, privesc]
---

# 7-Zip — wildcard and @lists for file reads

**English** | [🌐 Español](7z-wildcard-file-read.md)

## Concept

`7za` treats an argument starting with `@` as a file list and prints errors while reading it. If a root script runs `7za ... -- *`, create `@list` and a symlink with the same name to leak the target's contents.

## When it applies

- A root script uses `7za` with a wildcard.
- The working directory is writable.
- `--` does not disable `@` processing.

## Procedure

1. Identify the command and directory.
2. Create `@x` and a symlink `x` to the target.
3. Run the root script.
4. Rebuild the file from the error messages.

## Commands

```bash
touch @0xdf; ln -fs /root/.ssh/id_rsa 0xdf
sudo usage_management
# strip ' : No more files' and rebuild the key
```

## Variants

- `@` lists with several files.
- Symlinks to `/etc/shadow` or configuration.
- Chain with `tar` or `rsync` wildcards.

## Limitations

- The script may use absolute paths without a wildcard.
- Modern `7za` may change `@` handling.
- The directory may not be writable.

## Mitigation

- Avoid wildcards; use `find -print0` and `xargs -0`.
- Do not run backups as root.
- Use `--` and validate file names.

## Detection

- `@*` files in backup directories.
- `7za` errors containing file contents.
- Off-hours backup runs.

## CTF case: listfile in a periodic backup

On CTF, `/backup/backup.sh` runs `7za a /backup/$filename.zip -t7z -snl -p$pass -- *` every minute from a writable directory. Create an `@0xdf` file and an `0xdf` symlink to `/root/root.txt`; the wildcard expands `@0xdf`, `7za` treats it as a list and the error includes the target contents. The script clears the log at the end, so follow it with `tail -f` from another session.

```bash
touch @0xdf
ln -fs /root/root.txt 0xdf
# wait for the cron and read the log before it is cleared
```

The same idea works when the script compresses a whole directory with `*` and the attacker can create files there. The key is that `@` is processed even after `--`.

## References

- [HackTricks — 7z wildcard](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/wildcards-spare-tricks.html)
- [0xdf — Usage](https://0xdf.gitlab.io/2024/08/10/htb-usage.html)
- [p7zip — command line](https://p7zip.sourceforge.net/)
- [0xdf — CTF](https://0xdf.gitlab.io/2019/07/20/htb-ctf.html)
- [7-Zip — command line](https://7-zip.org/)
