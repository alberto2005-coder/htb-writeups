---
topic: TTY pushback — command injection with TIOCSTI
tags: [linux, tty, tiocsti, sudo, postgresql, privesc]
---

# TTY pushback — command injection with TIOCSTI

[🌐 Español](tty-pushback-tiocsti.md) | **English**

## Concept

`TIOCSTI` writes bytes into a terminal's input buffer. A child process can inject commands that the parent shell reads when it regains control. If the parent is a root shell that ran `su` or `sudo` interactively, the commands execute as root without passing the child's authentication.

## When it applies

- A privileged process spawns an interactive shell or `su`.
- The user controls a `.profile`, `.bashrc` or script executed in that session.
- The TTY is shared between child and parent.
- `dev.tty.legacy_tiocsti` is enabled (the default on many kernels).

## Procedure

1. Confirm the privileged process uses an interactive TTY.
2. Gain write access to a file executed when the child session starts.
3. Inject the desired commands into the parent TTY with `TIOCSTI`.
4. Wait for the privileged process to exit and the shell to read the buffer.

## Commands

```python
import fcntl, termios
for ch in b"cp /bin/bash /tmp/root; chmod 6777 /tmp/root\n":
    fcntl.ioctl(0, termios.TIOCSTI, bytes([ch]))
```

```bash
# one-liner alternative
python3 -c 'import fcntl,termios; [fcntl.ioctl(0,termios.TIOCSTI,bytes([c])) for c in b"id\n"]'
```

In PostgreSQL, write the service user's `.profile`:

```sql
COPY (SELECT 'python3 -c "..."') TO '/var/lib/postgresql/.profile';
```

## Variants

- Inject into the service user's `.bashrc` or `.profile`.
- Use `script` or `expect` to keep the TTY.
- Abuse a `su` launched by a cron or management script.
- Combine with `sudo -i` when the TTY is shared.

## Limitations

- Requires an interactive TTY in the same session group.
- `TIOCSTI` may be disabled by the kernel.
- The buffer is lost if the session closes.
- SELinux or seccomp may block the call.

## Mitigation

- Disable `TIOCSTI` with `dev.tty.legacy_tiocsti=0`.
- Avoid interactive shells in privileged scripts.
- Do not allow writes to service accounts' `.profile`/`.bashrc`.
- Use `sudo` with specific commands and `use_pty`.

## Detection

- `ioctl` calls with `TIOCSTI` (auditd, seccomp).
- Unexpected commands run by root after `su`.
- Changes to database users' `.profile`.
- Child processes writing to the parent TTY.

## References

- [man — ioctl_tty](https://man7.org/linux/man-pages/man2/ioctl_tty.2.html)
- [Linux kernel — legacy_tiocsti](https://www.kernel.org/doc/html/latest/admin-guide/sysctl/kernel.html)
- [0xdf — Download](https://0xdf.gitlab.io/2023/11/11/htb-download.html)
