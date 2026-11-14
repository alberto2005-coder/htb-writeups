---
topic: Redis por socket Unix en Nginx
tags: [web, nginx, redis, unix-socket, proxy-pass]
---

# Redis por socket Unix en Nginx

[🌐 Español](nginx-redis-socket.md) | **English**

## Concept

A `proxy_pass` rule pointing to a Redis Unix socket lets an HTTP request become RESP commands. If the socket does not require authentication, an attacker can read or write keys, sessions and configuration.

## When it applies

- Nginx forwards a prefix to `unix:/var/run/redis/redis.sock`.
- Redis listens only on the socket, but Nginx exposes it.
- The application uses Redis for sessions, roles or cache.

## Procedure

1. Review Nginx configuration and reachable sockets.
2. Identify an endpoint that reaches the `proxy_pass`.
3. Send RESP commands in the body or path, depending on the rule.
4. Read session keys or modify a role.
5. Write a file if Redis has a writable directory.

```bash
curl -s "http://<HOST>/redis/" --data-binary $'PING\r\n'
```

## Variants

- `proxy_pass` with a URI that preserves the prefix.
- Redis with a weak or reused `requirepass`.
- Webshell write through `CONFIG SET dir` and `SAVE`.

## Limitations

- Nginx may normalize or block the method.
- Redis may run in protected mode.
- The socket may have restrictive permissions.

## Mitigation

- Do not expose Redis through Nginx.
- Require authentication and `protected-mode`.
- Run Redis as a user without webroot write access.

## Detection

- HTTP requests containing `PING`, `GET`, `SET` or `CONFIG`.
- Socket access from Nginx.
- New files in the Redis working directory.

## References

- <https://redis.io/docs/latest/operate/oss_and_stack/management/security/>
- <https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_pass>
- <https://attack.mitre.org/techniques/T1190/>
