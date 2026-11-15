---
topic: Linux — memory mmap and credential overwrite
tags: [linux, kernel, mmap, cred, privesc]
---

# Linux — memory mmap and credential overwrite

[🇪🇸 Español](mmap-cred-overwrite.md) | **English**

## Concept

A module or device that allows `mmap` over physical memory breaks kernel isolation. If the attacker can map and write arbitrary memory, they can locate their process's `cred` structure and set `uid` and `gid` to 0 without running a SUID binary.

## When it applies

- A `/dev/<name>` device created by a vulnerable module exists.
- The device allows `mmap` with `PROT_WRITE` and `MAP_SHARED`.
- SMEP/SMAP and `/dev/mem` or `perf_event` restrictions are absent.

## Procedure

1. Enumerate devices and modules with `ls -l /dev`, `dmesg` and `lsmod`.
2. Open the device and map a page.
3. Find the current process's `cred` structure.
4. Write `uid=0` and `gid=0`, then verify with `id`.

```c
int fd = open("/dev/dhid", O_RDWR);
void *map = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
// locate cred and overwrite uid/gid
```

## Variants

- Write directly to `/dev/mem` or `/dev/kmem`.
- Use `/proc/kcore` when readable.
- Modify `modprobe_path` or a kernel function.

## Limitations

- Requires a vulnerable device or module.
- KASLR makes structures harder to locate.
- A patched kernel blocks physical memory `mmap`.

## Mitigation

- Remove modules that expose physical memory.
- Enable SMEP, SMAP, KASLR and `CONFIG_STRICT_DEVMEM`.
- Restrict `/dev` permissions and audit third-party modules.

## Detection

- `mmap` of non-standard devices by user processes.
- UID changes without `setuid` or `sudo`.
- Modules loaded outside the inventory.

## References

- [0xdf — Smasher2](https://0xdf.gitlab.io/2019/12/14/htb-smasher2.html)
- [Linux kernel — credentials](https://www.kernel.org/doc/html/latest/security/credentials.html)
- [CWE-123 — Write-what-where Condition](https://cwe.mitre.org/data/definitions/123.html)
