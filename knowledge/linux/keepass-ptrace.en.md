---
topic: KeePass — capturing the master password with ptrace
tags: [linux, keepass, kpcli, ptrace, strace, credentials, mailroom]
---

# KeePass — capturing the master password with ptrace

[🌐 Español](keepass-ptrace.md) | **English**

## Idea

KeePass databases are encrypted with a master password and, when opened from a console, that password is typed into the process's terminal. On Linux, `strace` can read another same-user process's `read` calls and capture what is typed. On Mailroom, `matthew` opened `personal.kdbx` with `kpcli` and tracing the process revealed the master password, which yielded root's.

## When it applies

- The victim opens a password manager on the same host.
- The attacker has a shell as the same user or as root.
- `kernel.yama.ptrace_scope` allows attaching (0 or 1).
- The manager reads the password from standard input or the terminal.

## Procedure

1. Enumerate processes and locate the manager (`kpcli`, `keepassxc-cli`).
2. Check the `ptrace` scope.
3. Attach `strace` to the process and filter `read`.
4. Find the master password in the output.
5. Open the database with `kpcli` and read the entries.
6. Use root's password or the SSH key found.

## Commands

```bash
ps aux | grep -i keep
cat /proc/sys/kernel/yama/ptrace_scope
strace -f -e trace=read,write -s 200 -p <PID>
```

```bash
kpcli --kdb personal.kdbx
# inside: ls, cd <group>, show -f <entry>
```

```text
read(0, "<PASSWORD>\n", 4096) = <N>
```

## Variants

- Dump process memory with `gdb -p` and search for strings.
- If the manager uses a socket, intercept traffic with `socat`.
- As root, read `/proc/<PID>/mem` or use `gcore`.
- Combine with a keylogger if input bypasses `read`.

## Limitations

- `ptrace_scope=2` or `3` blocks attaching to other users' processes.
- With `hidepid` the victim's processes are invisible.
- The manager may wipe the entry from memory after use.
- Waiting for the victim to type the password is required.

## Mitigation

- Set `kernel.yama.ptrace_scope=2` or `3`.
- Use `hidepid=2` on `/proc` and separate sessions per user.
- Prefer managers with agent integration and no terminal password entry.
- Rotate master passwords and use MFA or keyfiles.
- Never share sessions or run managers on compromised hosts.

## Detection

- `strace` or `gdb` processes attached to password managers.
- Reads of `/proc/<PID>/mem` by unusual processes.
- `ptrace` events in auditd (`-a always,exit -F arch=b64 -S ptrace`).
- `.kdbx` databases opened by users other than the owner.

## References

- [KeePass — Security](https://keepass.info/help/base/security.html)
- [kpcli](https://github.com/soremwar/kpcli)
- [Linux — Yama ptrace](https://www.kernel.org/doc/html/latest/admin-guide/LSM/Yama.html)
- [0xdf — Mailroom](https://0xdf.gitlab.io/2023/08/19/htb-mailroom.html)
- [Mailroom writeup](../../machines/linux/mailroom/README.en.md)
