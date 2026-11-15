---
topic: gdbserver and screen — execution and root session
tags: [linux, gdbserver, screen, debugging, privesc]
---

# gdbserver and screen — execution and root session

**English** | [🌐 Español](gdbserver-screen-root.md)

## Concept

`gdbserver` attaches to a process and executes functions in its context. If it listens on loopback but is reachable from a vulnerable application, it becomes code execution. A root `screen` session with multiuser enabled allows attaching without credentials and obtaining its shell.

## When it applies

- `/proc/net/tcp` or a local scan reveals `gdbserver`.
- The vulnerable application allows SSRF or reading `/proc`.
- Root keeps a `screen` session with multiuser enabled.

## Procedure

1. Enumerate processes and sockets from `/proc`.
2. Reach `gdbserver` and attach to the process.
3. Run a command with `call system`.
4. Find `screen` sessions and attach to root's.

## Commands

```bash
cat /proc/net/tcp
ps aux | grep -i gdb
gdb -q -ex "target remote 127.0.0.1:1337" -ex "call system(\"id\")"
screen -ls
screen -x root/root
```

## Variants

- Use `gdbserver --attach` on a privileged process.
- Combine it with an SSH tunnel or proxy to reach loopback.
- Abuse `screen -x` or `-r` when multiuser is enabled.

## Limitations

- `gdbserver` must accept the connection and the process must be debuggable.
- The `screen` session may require the same user or multiuser.
- SELinux/AppArmor may block `ptrace`.

## Mitigation

- Do not expose `gdbserver`; remove it from production.
- Disable `screen` multiuser and close root sessions.
- Restrict `ptrace` and `/proc` reads from the application.

## Detection

- Connections to `gdbserver` ports.
- `ptrace` or `call system` from debug processes.
- Open root `screen` sessions and unusual attachments.

## References

- [0xdf — Backdoor](https://0xdf.gitlab.io/2022/04/23/htb-backdoor.html)
- [GNU Screen — manual](https://www.gnu.org/software/screen/manual/screen.html)
- [GDB — Remote debugging](https://sourceware.org/gdb/current/onlinedocs/gdb.html/Remote-Debugging.html)
