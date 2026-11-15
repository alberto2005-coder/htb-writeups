---
topic: Linux — CAP_DAC_READ_SEARCH in containers
tags: [linux, docker, capabilities, dac-read-search, container-escape]
---

# Linux — CAP_DAC_READ_SEARCH in containers

**English** | [🌐 Español](cap-dac-read-search.md)

## Concept

`CAP_DAC_READ_SEARCH` bypasses file and directory read permissions. A container with this capability and a host mount can read keys, configuration and password hashes; if write access also exists, it can modify privileged tasks and execute as root.

## When it applies

- `capsh --print` shows `cap_dac_read_search`.
- The container mounts host directories or shares the process namespace.
- The goal is to read secrets or write a privileged task.

## Procedure

1. Enumerate capabilities and mounts.
2. Read protected host files with the capability.
3. Find a write path or a task that runs as root.
4. Create or modify the file and wait for execution.

## Commands

```bash
capsh --print
mount | grep -E "host|docker|/root"
cat /proc/1/root/etc/shadow 2>/dev/null
# If writable, create a task or key
ls -la /proc/1/root/root/.ssh/
```

## Variants

- Read SSH keys and reuse them outside the container.
- Modify a host cron or startup script.
- Combine it with `CAP_DAC_OVERRIDE` for writing.

## Limitations

- The capability only affects reads, not writes.
- The container must see the host path.
- SELinux/AppArmor may block access.

## Mitigation

- Drop `CAP_DAC_READ_SEARCH` from containers.
- Mount secrets read-only and use user namespaces.
- Enforce seccomp/AppArmor and review capabilities.

## Detection

- Containers reading `/etc/shadow` or host keys.
- `CAP_DAC_READ_SEARCH` used by non-root processes.
- Accesses to `/proc/1/root` from containers.

## References

- [Linux — capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [Docker — Runtime privileges](https://docs.docker.com/engine/containers/run/#runtime-privilege-and-linux-capabilities)
- [0xdf — Talkative](https://0xdf.gitlab.io/2022/08/27/htb-talkative.html)
