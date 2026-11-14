---
topic: Scheduled task hijacking
tags: [linux, cron, systemd, privesc, persistence, writable-scripts]
---

# Scheduled task hijacking

**English** | [🇪🇸 Español](task-scheduler-hijack.md)

## Concept

A privileged process periodically runs a script, binary or command that a lower-privileged user can modify. By changing the content or the referenced path, the attacker gains execution with the task's privileges.

## When it applies

- `cron`, `systemd timers`, `at` or application tasks.
- Scripts in `/opt`, `/usr/local` or user directories with write access.
- Commands with relative paths or a manipulable `PATH`.
- Tasks that restore files automatically.

## Procedure

1. Enumerate tasks with `pspy`, `crontab -l`, `/etc/crontab` and `systemctl list-timers`.
2. Review each script's owner and permissions.
3. Check whether the content is restored or overwritten.
4. Replace the script with a controlled action.
5. Wait for execution and verify the result.

```bash
pspy64 -pf -i 1000
ls -l /opt/backup.sh /usr/local/bin/*.py
find / -writable -type f 2>/dev/null | grep -E 'cron|systemd|/opt/'
```

## Variants

- Script writable by a group or by everyone.
- Writable directory with a script invoked by path.
- `PATH` with a controlled directory before the legitimate binary.
- `tar` or `rsync` wildcard in a writable directory.
- Task that restores the original script after each run.

## Limitations

- The task must run with higher privileges.
- Restoration may overwrite the change before execution.
- SELinux/AppArmor may block writes.
- The interval between runs may be long.

## Mitigation and detection

- Keep scripts in non-writable paths owned by root.
- Use absolute paths and a safe `PATH`.
- Monitor cron/systemd script changes with `auditd`.
- Alert on unexpected cron-spawned processes and changes under `/etc/cron*`.

## References

- <https://attack.mitre.org/techniques/T1053/003/>
- <https://attack.mitre.org/techniques/T1053/006/>
- <https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html>
- <https://github.com/DominicBreuker/pspy>
