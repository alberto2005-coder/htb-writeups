---
title: "DirtyPipe (CVE-2022-0847): writing into the page cache"
tags: [linux, kernel, dirtypipe, cve-2022-0847, privesc, pipe]
---

# DirtyPipe (CVE-2022-0847): writing into the page cache

**English** | [🇪🇸 Español](kernel-dirty-pipe.md)

## 1. When to look here

Linux kernel **5.8 or later** without the March 2022 fix. An unprivileged user can overwrite read-only files, including SUID binaries and configuration files, without touching the heap or needing KASLR.

## 2. The bug

When `splice()` moves a file page into a pipe, the pipe buffer keeps the `PIPE_BUF_FLAG_CAN_MERGE` flag from a previous operation. A later `write()` believes it can merge data into the buffer and writes into the file's **page cache**, even though the descriptor is `O_RDONLY`.

```text
pipe full -> every buffer has CAN_MERGE
pipe drained -> buffers freed, flag remains
splice(file, offset-1, 1) -> buffer points at the file page
write(payload) -> writes into the page cache from offset
```

It is a data write, not a kernel structure write: SMEP, SMAP, KASLR and SLUB mitigations do not apply.

## 3. Versions

- Affected: 5.8 and later, up to 5.16.11, 5.15.25 and 5.10.102 (and equivalent branches).
- Not affected: < 5.8.
- EOL branches (5.9, for example) have no fix: they stay vulnerable.

## 4. Limits

- Byte 0 of a page cannot be written (splice must move at least 1 byte).
- Files cannot grow; only overwrite within their size.
- The change lives in the page cache until the page is evicted or the system reboots.
- Writing into a mapped file can corrupt processes that already loaded it.

## 5. Typical uses

1. **SUID binary**: overwrite the entry point or a function to spawn a SUID shell.
2. **`/etc/passwd`**: change root's hash and use `su`; only works if `su`/`login` are usable.
3. **`modprobe_path` via page cache**: if a binary the kernel runs as root can be written (`/sbin/modprobe`), place shellcode at its entry and trigger it with an unknown `binfmt`.
4. **Configuration files**: SSH keys, cron, systemd units.

### Busybox and modprobe chain

- `/sbin/modprobe` is often a symlink to busybox.
- Busybox entry point: `readelf -h`; file offset = entry - load base.
- The offset must not be page-aligned.
- The file that triggers `request_module()` needs **non-printable** magic; if the first four bytes are printable ASCII, the kernel assumes text and skips modprobe.
- `call_usermodehelper()` runs modprobe with stdout/stderr on `/dev/null`: the payload must write to a file.
- If the payload breaks busybox, `system()` and `/bin/sh` stop working; use direct syscalls.

## 6. Detection

- `splice` from a read-only file followed by `write` to the same pipe.
- System binary contents changing without a prior file write (integrity, IMA, `rpm -Va`).
- Modified `modprobe_path` and `/sbin/modprobe` executions with no real module load.
- Execution of files with non-printable magic, or `binfmt-*` invoked from a user process.
- Page cache pages whose content does not match the on-disk hash.

## 7. Mitigation

- Update to 5.16.11, 5.15.25, 5.10.102 or later; there is no reliable workaround.
- Do not run binaries from writable paths; read-only `/usr` and `/bin` help detection, not prevention.
- Binary and `modprobe_path` integrity; audit `request_module`.
- Containers: the bug allows escaping the image to the host when they share a vulnerable kernel.

CWE-665 (improper initialization), MITRE T1068 (exploitation for privilege escalation). References: dirtypipe.cm4all.com, NVD CVE-2022-0847 and the CISA alert.
