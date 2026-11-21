---
topic: SUID — file descriptor and crash dump reads
tags: [linux, suid, file-descriptors, core-dump, crash, secret, privesc]
---

# SUID — file descriptor and crash dump reads

**English** | [🌐 Español](suid-fd-crashdump.md)

## Idea

A SUID binary that opens a privileged file and does not close the descriptor allows access to it through `/proc/<PID>/fd/<N>`. File permissions still apply: it reads readable files inside directories that cannot be traversed, not a mode-400 file. If it also produces a core dump, content read as root ends up in the dump, which may be readable. On Secret, `count` read `/root/.profile` through the descriptor; `root.txt` appeared in the crash dump.

## When it applies

- A SUID binary opens files the user cannot read.
- The process leaves descriptors open or spawns a child.
- Core dumps are enabled and written to an accessible path.
- `kernel.core_pattern` or `apport` do not restrict the dump.

## Procedure

1. Identify the SUID and its source if available.
2. Run it against a privileged file and watch `/proc`.
3. Read `/proc/<PID>/fd/<N>` when the file mode allows it.
4. Alternatively, crash it and locate the core.
5. Extract content with `strings` or `grep`.

## Commands

```bash
/opt/count
ls -l /proc/<PID>/fd/
cat /proc/<PID>/fd/<N>  # only if the user may read the file
```

```bash
ulimit -c unlimited
cat /proc/sys/kernel/core_pattern
ls -l /var/crash/
strings /var/crash/_opt_count.*.crash | grep -i 'flag\|root'
```

## Variants

- `/proc/<PID>/maps` and `mem` when permissions allow.
- `gdb -p <PID>` to attach to a SUID process.
- `ptrace` a child when the binary allows it.
- Core dump from `abort()` or a segmentation fault.
- Ubuntu's `apport` writes to `/var/crash` with controlled permissions.

## Limitations

- `fs.suid_dumpable` may block SUID core dumps.
- `core_pattern` may pipe the dump or use an inaccessible path.
- The descriptor may close before it can be read.
- `ptrace` may be restricted by `yama`.
- The binary may clean up temporary files.

## Mitigation

- Close descriptors before running code or exiting.
- Set `fs.suid_dumpable=0` and a safe `core_pattern`.
- Restrict `ptrace` with `kernel.yama.ptrace_scope`.
- Remove unnecessary SUID bits and review those that open files.
- Use `O_CLOEXEC` on descriptors.

## Detection

- Reads of `/proc/<PID>/fd` by non-owner users.
- Core dumps from SUID processes.
- `gdb` or `strace` attached to privileged binaries.
- Changes to `core_pattern` or `ulimit`.
- Access to `/var/crash` with sensitive content.

## References

- [0xdf — Secret](https://0xdf.gitlab.io/2022/03/26/htb-secret.html)
- [Linux — proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html)
- [Linux — core(5)](https://man7.org/linux/man-pages/man5/core.5.html)
- [Secret writeup](../../machines/linux/secret/README.en.md)
