---
topic: Dirty COW — writing to read-only memory (CVE-2016-5195)
tags: [linux, kernel, dirty-cow, cve-2016-5195, privesc, popcorn]
---

# Dirty COW — writing to read-only memory (CVE-2016-5195)

[🌐 Español](dirty-cow.md) | **English**

## Concept

Dirty COW is a race condition in Linux's copy-on-write handling. It allows writing to a page mapped read-only, even inside a file the user cannot modify. The classic use is overwriting `/etc/passwd` to add a passwordless root user or change root's password, and it has also been used to patch setuid binaries in memory.

Affects kernels from 2.6.22 to 4.8.3 (with distribution backports).

## When it applies

- Vulnerable kernel without the distribution patch.
- A readable, mappable system file or binary.
- A compiler, or a prebuilt exploit for the architecture.
- On Popcorn it was considered as an alternative to the PAM escalation.

## Procedure

1. Confirm the kernel version (`uname -a`).
2. Check that the exploit compiles for that architecture.
3. Run the `/etc/passwd` exploit or the setuid-binary variant.
4. Log in with the created user or run the modified binary.
5. Restore the original file if it was changed.

## Commands

```bash
uname -a
gcc -pthread dirty.c -o dirty -lcrypt
./dirty <PASSWORD>
su firefart
```

Setuid variant:

```bash
gcc -pthread cow.c -o cow
./cow /usr/bin/sudo
```

## Variants

- firefart's `dirtycow`: creates a UID 0 `firefart` entry in `/etc/passwd`.
- `dirtyc0w`: writes to a read-only file to change its contents.
- Patch a setuid binary so it executes a shell.
- Use `ptrace` or `/proc/self/mem` instead of `mmap`.

## Limitations

- The kernel must be vulnerable; distribution patches usually fix it.
- The race can fail and needs retries.
- Some configurations (SELinux, read-only root) block the target.
- Modifying `/etc/passwd` is noisy and can break the system.

## Mitigation

- Update the kernel to 4.8.3 or later, or the distribution patch.
- Apply integrity monitoring (AIDE, IMA) to `/etc/passwd` and setuid binaries.
- Run containers as non-root with a read-only root filesystem.
- Monitor writes to system files.

## Detection

- Unexpected changes to `/etc/passwd`, `/etc/shadow` or setuid binaries.
- Processes mapping system files and writing to `/proc/self/mem`.
- New UID 0 users.
- Exploit compilation in `/tmp` and repeated execution.

## References

- [NVD — CVE-2016-5195](https://nvd.nist.gov/vuln/detail/CVE-2016-5195)
- [Dirty COW — dirtycow.ninja](https://dirtycow.ninja/)
- [0xdf — Popcorn](https://0xdf.gitlab.io/2018/04/21/htb-popcorn.html)
- [Popcorn writeup](../../machines/linux/popcorn/README.en.md)
