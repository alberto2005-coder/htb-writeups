---
topic: Containers — escape through a shared cwd
tags: [linux, docker, container, jail-escape, cwd]
---

# Containers — escape through a shared cwd

**English** | [🌐 Español](container-jail-cwd-escape.md)

## Concept

A container using `chroot` without process isolation can expose `/proc/self/cwd` as a symlink to the host directory. If `cwd` points outside the jail, host files can be read without root.

## When it applies

- The container shares the filesystem or process space.
- `/proc` is mounted and `cwd` points to a host path.
- Commands can run inside the container.

## Procedure

1. List `/proc/self/cwd` and its links.
2. Read relative paths from the host `cwd`.
3. Look for SSH keys, configuration or secrets.
4. Use the key to enter the host.

## Commands

```bash
ls -l /proc/self/cwd
cat /proc/self/cwd/../../home/jack/.ssh/id_rsa
find /proc/self/cwd -maxdepth 3 -name '*.key' 2>/dev/null
```

## Variants

- `/proc/1/root` to escape the jail.
- `/proc/self/mountinfo` to map the host.
- Chain with a host root process.

## Limitations

- An isolated PID namespace hides host `/proc`.
- `cwd` may be inside the container.
- `hidepid` mounts limit reads.

## Mitigation

- Isolate with namespaces and `pivot_root`.
- Do not share the host filesystem.
- Run rootless containers with seccomp.

## Detection

- Reads of `/proc/*/cwd` or `/proc/1/root`.
- SSH key access from a container.
- Container processes reading host paths.

## References

- [0xdf — RainyDay](https://0xdf.gitlab.io/2023/02/18/htb-rainyday.html)
- [Docker — security](https://docs.docker.com/engine/security/)
- [HackTricks — container escape](https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/docker-security/index.html)
