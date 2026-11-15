---
title: Temporary-file race — reading /etc/shadow
tags: [linux, race-condition, symlink, privesc, tmp]
---

# Temporary-file race — reading /etc/shadow

[🇪🇸 Español](tmp-race-shadow-read.md) | **English**

## Concept

A privileged script that copies `/etc/shadow` to a predictable temporary file and deletes it after authentication allows a race. If the attacker replaces the file with a symlink to a readable destination, or opens it before deletion, they get the hashes.

## When it applies

- `sudo -l` shows a script that copies or writes files as root.
- The destination is in `/tmp`, `/dev/shm` or the user's directory.
- The filename is fixed or follows a guessable pattern.

## Procedure

1. Read the script and locate temporary-file creation.
2. Watch the directory with `inotifywait`.
3. As soon as it appears, copy it or replace it with a symlink.
4. Crack the hashes or use the file for another escalation.

```bash
inotifywait -m -e create -e moved_to /tmp &
while true; do
  for f in /tmp/.shadow* /tmp/shadow*; do
    [ -f "$f" ] && cp "$f" /dev/shm/leak 2>/dev/null && break
  done
done
```

## Variants

- Symlink to a file the attacker controls so the script writes as root.
- A missing `O_NOFOLLOW` enables the symlink.
- The race also works for `authorized_keys` or backup jobs.

## Limitations

- The file may be mode 600 and deleted very quickly.
- `fs.protected_symlinks` and `fs.protected_regular` mitigate part of the attack.
- Local access is required and the script must run as root.

## Mitigation and detection

- Use `mkstemp()` and `O_NOFOLLOW`, and unlink safely.
- Do not copy `/etc/shadow`; use PAM or `getspnam`.
- Mount `/tmp` with `nosuid,nodev` and protect symlinks.
- Audit privileged script runs and temporary files.

## References

- <https://man7.org/linux/man-pages/man7/inotify.7.html>
- <https://cwe.mitre.org/data/definitions/367.html>
- <https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html>
