---
topic: Escalada por script de backup en cron
tags: [linux, cron, backup, privesc, writable]
---

# Escalada por script de backup en cron

**English** | [🇪🇸 Español](cron-backup-privesc.md)

## Concept

A cron job runs a backup script as root that the user can modify. Add a line and the next cycle executes the command with root privileges.

## When it applies

- Backup scripts in `/usr/local/bin`, `/opt` or home with write permissions.
- Cron jobs or systemd timers running unprotected scripts.
- Backup directories with wildcards or controllable paths.

## Procedure

1. Enumerate cron and timers with `pspy`, `crontab -l` and `/etc/cron*`.
2. Review permissions and ownership of executed scripts.
3. Add a payload that copies SUID bash or spawns a shell.
4. Wait for execution and use the resulting shell.

```bash
pspy -f
ls -l /usr/bin/backup.sh /etc/cron.d/
printf 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash\n' >> /usr/bin/backup.sh
/tmp/rootbash -p
```

## Variants

- `tar` with wildcards and checkpoint.
- `rsync` with `--rsh` or controllable paths.
- systemd timer with a writable script.
- PATH hijack inside the script.

## Limitations

- The script must be writable by the user.
- The job must run as root.
- The next cycle may take time.

## Mitigation and detection

- Root-owned backup scripts with no write access for others.
- Use absolute paths and clean environments.
- Monitor script changes and cron child processes.

## References

- <https://gtfobins.github.io/>
- <https://attack.mitre.org/techniques/T1053/003/>
- <https://man7.org/linux/man-pages/man5/crontab.5.html>
