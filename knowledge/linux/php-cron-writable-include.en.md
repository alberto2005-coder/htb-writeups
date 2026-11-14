---
topic: PHP — writable include in a root cron
tags: [linux, php, cron, include, privesc]
---

# PHP — writable include in a root cron

**English** | [🌐 Español](php-cron-writable-include.md)

## Concept

A PHP script run by cron as root may include a configuration file or library that an unprivileged user can modify. If the content is interpreted as PHP, a configuration change becomes code execution with the cron user privileges.

## When it applies

- A monitor, backup task or PHP panel runs as root.
- The script uses `include`, `require` or `eval` on configuration paths.
- One of those files is writable by `www-data` or the current user.

## Procedure

1. Watch processes and cron with `pspy` to locate root executions.
2. Read the main script and identify its `include` paths.
3. Check permissions with `find` and `ls -l`.
4. Add a PHP statement that creates a SUID shell and wait for the next run.

## Commands

```bash
pspy64 -pf -i 1000
grep -RInE "include|require|eval" /opt/website-monitor
find /opt/website-monitor -writable -type f -ls
# Test payload
printf "%s\n" "<?php system("cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash"); ?>" >> file.php
```

## Variants

- Write a webshell into the included file when a web server sits in front.
- Use `auto_prepend_file` or a log path when the include is indirect.
- Modify a Composer library or configuration file loaded by the script.

## Limitations

- The cron may run every few minutes; wait for it.
- `disable_functions` or a strict `open_basedir` can block the shell.
- If the file is replaced or hash-checked, the change does not persist.

## Mitigation

- Mount the monitor and its includes read-only.
- Run the cron as an unprivileged user and review the trust chain.
- Apply `open_basedir`, `disable_functions` and integrity alerts.

## Detection

- Changes to PHP configuration files outside deployments.
- `php` child processes of `cron` creating SUID files or spawning shells.
- Writes by `www-data` into system directories.

## References

- [0xdf — Alert](https://0xdf.gitlab.io/2025/03/22/htb-alert.html)
- [CWE-94 — Code Injection](https://cwe.mitre.org/data/definitions/94.html)
- [PHP — include](https://www.php.net/manual/en/function.include.php)
