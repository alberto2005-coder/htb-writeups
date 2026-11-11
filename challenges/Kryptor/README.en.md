---
challenge: Kryptor
category: Challenge
type: pwn
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [pwn, kernel, dirtypipe, cve-2022-0847, modprobe, busybox, kaslr]
---

# Kryptor — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired based on public writeups; not verified with an HTB session.
> No flags, instance offsets or challenge binary.

## TL;DR

A kernel exploitation challenge on **Linux 5.9.10** with SMEP, SMAP, KASLR, KPTI and `oops=panic`. The `kryptor.ko` module has a real race (a mutex initialised but never locked), yet every UAF chain hits `SLAB_FREELIST_HARDENED`, `HARDENED_USERCOPY`, `STRICT_MODULE_RWX` and `kptr_restrict`. The working path is **DirtyPipe (CVE-2022-0847)**: overwrite busybox's entry point in the page cache and trigger `modprobe` so the kernel runs it as root.

## Brief and surface

- **Pwn** category, **Insane** difficulty, booted through a serial console with QEMU.
- Ships `bzImage`, `initramfs.cpio.gz`, `run.sh` and `kryptor.ko` (not stripped).
- The goal is to read a file under `/root` whose name is a random SHA-256, mode `0400`.

```bash
file bzImage kryptor.ko
strings bzImage | grep -m1 "Linux version"
```

```text
Linux version 5.9.10 (x86_64)
```

That detail decides everything: 5.9.10 predates the DirtyPipe fixes.

## Recon

`init` mounts `/proc`, `/sys` and `/dev`, creates the flag file, loads the module and starts a shell as uid 1000 (`johnny`):

```sh
FLAG=$(head -n 100 /dev/urandom | sha256sum | awk '{printf $1}')
mv /root/temp /root/$FLAG
chmod 0400 /root/$FLAG
insmod /kryptor.ko
chmod 666 /dev/kryptor
setsid cttyhack setuidgid 1000 /bin/sh
```

- `/dev/kryptor` is world-accessible.
- `oops=panic`: any kernel fault reboots the VM, no second chances.
- Two CPUs allow real races between threads.

## Module analysis

`kryptor_ioctl` copies a `0x18`-byte request (`index`, `data_ptr`, `auth_ptr`), checks a SHA-256 against an embedded token and dispatches three commands:

| Command | Operation |
|---|---|
| `0xEEEEEEEE` | allocate from `kmalloc-256`, copy `0x100` bytes and XOR-encrypt |
| `0xDDDDDDDD` | decrypt in place, copy to user and re-encrypt |
| `0xFFFFFFFF` | `kfree` and NULL the pointer |

Two defects stand out:

- `init_kryptor` initialises `kryptor_lock`, but `kryptor_ioctl` **never** calls `mutex_lock` or `mutex_unlock`.
- `n_allocations` is incremented on ENCRYPT and never decremented on DELETE: the module allows four allocations in total.

With `userfaultfd`, `copy_from_user` can be stalled mid-ENCRYPT while DECRYPT or DELETE runs on the same index: UAF read and write, plus a double free.

## Why the UAF is not enough

Every attempt to turn the race into root hits a different mitigation:

| Mitigation | Effect |
|---|---|
| `CONFIG_SLAB_FREELIST_HARDENED` | freelist pointers are XOR-obfuscated; a raw pointer decodes as non-canonical |
| `CONFIG_HARDENED_USERCOPY` | `copy_to_user` checks the object size; reading past 256 bytes aborts |
| `CONFIG_STRICT_MODULE_RWX` | module `.data`/`.bss` become read-only after init |
| `kptr_restrict` | `/proc/kallsyms` shows zeros to uid 1000; no procfs KASLR leak |
| `oops=panic` | one kernel page fault reboots the machine |

The practical conclusion: the module is a defended decoy; the exploitable bug is in the kernel itself.

## DirtyPipe (CVE-2022-0847)

The bug lives in the pipe subsystem: when `splice()` moves a file page into a pipe, the `PIPE_BUF_FLAG_CAN_MERGE` flag is not cleared. A later `write()` believes it is filling a pipe gap and writes **straight into the file's page cache**, even though the descriptor was read-only.

Sequence:

1. Fill the pipe to capacity so every buffer gets `CAN_MERGE`.
2. Drain it: buffers are freed, the flag stays.
3. `splice()` 1 byte from the target file at `offset - 1`.
4. `write()` the payload: it lands in the page cache from `offset`.

Limits: byte 0 of a page cannot be written, files cannot grow, and changes persist until the page is evicted.

## The bug and the chain

The system is busybox and `/sbin/modprobe` is a symlink to `/bin/busybox`. The ELF entry point is at `0x402070` and the load base is `0x400000`:

```text
file offset = 0x402070 - 0x400000 = 0x2070
```

`0x2070` is not the first byte of a page (`0x2070 % 0x1000 = 0x70`), so DirtyPipe can write there. The plan:

1. Overwrite `/bin/busybox`'s entry with positional shellcode (about 310 bytes).
2. Create a file with **non-printable** magic bytes (`\xff\xff\xff\xff`) and execute it.
3. The kernel finds no `binfmt`, calls `request_module("binfmt-ffff")` and runs `/sbin/modprobe` as root.
4. `modprobe` resolves to busybox; the kernel loads it from the corrupted page cache and runs the shellcode as uid 0.
5. The shellcode enumerates `/root` with `getdents64`, reads the flag file and copies it to `/home/johnny/flag`.
6. The exploit, still uid 1000, reads that file.

### Three gotchas

- **Printable magic bytes**: if the first four bytes are in `0x20–0x7e`, `search_binary_handler()` assumes text and skips `request_module()`. It fails silently, with no log.
- **`modprobe` with stdout on `/dev/null`**: the shellcode cannot print the flag; it must write it to a file.
- **Busybox corrupted for everyone**: the shellcode cannot use `system()` or `execve("/bin/sh")`, because `/bin/sh` is busybox too and would re-enter the corrupted code. Direct syscalls are required.

## Local reproduction

```bash
./run.sh
# inside the VM, as johnny
cat /proc/sys/kernel/modprobe      # /sbin/modprobe
readelf -h /bin/busybox | grep Entry
```

`readelf` should show `0x402070`; a different binary means recomputing the offset with the same subtraction.

## Exploitation

```c
/* Primitive summary, not the full exploit */
int fd = open("/bin/busybox", O_RDONLY);
int p[2]; pipe(p);
/* fill and drain the pipe so CAN_MERGE stays set */
splice(fd, &off_minus_1, p[1], NULL, 1, 0);
write(p[1], shellcode, sizeof(shellcode));   /* lands in the page cache */
```

- Build static with `musl-gcc` when the rootfs has no glibc.
- Upload the binary over the serial console (base64) and run it as `johnny`.
- The shellcode must open `/root` with `O_RDONLY|O_DIRECTORY` (`0x10000`), not `O_RDWR`.
- `/root` names are random: enumerate them, do not guess.

## Evidence

- `uname -r` or `strings bzImage` showing `5.9.10`.
- Boot/`checksec` with SMEP, SMAP, KASLR and KPTI.
- Exploit output with `FLAG_START`/`FLAG_END` and the read contents, never the real flag.

## Lessons learned

- A vulnerable module is not always the path: heap mitigations can close it while the kernel remains attackable elsewhere.
- DirtyPipe is a data attack: it never touches the heap and needs no KASLR, so it survives every SLUB protection.
- A static non-PIE binary's entry point is a stable target; compute the offset instead of copying it.
- The worst details are the silent ones: printable magic, stdout on `/dev/null`, recursive busybox.
- `oops=panic` changes the method: every attempt must be tested locally before touching remote.

## Mitigations and detection

- Update to 5.16.11, 5.15.25, 5.10.102 or later; the 5.9 branch has no such fix.
- Do not rely on KASLR for this bug: it needs no kernel addresses.
- Monitor `modprobe_path` and unexpected `/sbin/modprobe` executions; verify static binary integrity in the page cache.
- Alert on `splice` from read-only files followed by `write` to the same pipe, and on executions of files with non-printable magic.
- References: CVE-2022-0847, CWE-665, MITRE T1068 and T1547.006.

## References

- <https://www.echo8134.dev/w/054ee84a91fe02bb>
- <https://dirtypipe.cm4all.com/>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-0847>
- <https://www.cisa.gov/news-events/alerts/2022/03/10/dirty-pipe-privilege-escalation-vulnerability-linux>
