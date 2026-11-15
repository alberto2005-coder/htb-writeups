---
machine: Rope
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, pwn, format-string, got, rop, privesc]
---

# Rope — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A custom web server on `9999` allows directory traversal and leaks `puts` through a format string. Overwrite `puts`'s GOT entry with `system` and run a command. Locally, the `1337` service runs as root with canary, PIE and NX; leak the address and build a ROP chain to call `system`.

## Recon

```bash
nmap -Pn -sCV -p22,9999 <IP>
```

- `22/tcp` OpenSSH and `9999/tcp` an HTTP server written in C, not nginx.
- The response includes custom headers and a directory listing.
- `1337/tcp` only listens on localhost and runs a SUID/root binary.

## Enumeration

- `GET //etc/passwd` escapes the web root through the double slash.
- Server logs pass through `printf(user_input)`, producing a format string.
- `checksec` on the local binary shows canary, PIE and NX; the service runs as root.

## Foothold

Send `%p` repeatedly and locate `puts`'s GOT address. Write `system` with `%n` in two halves and request a path containing `; bash -c '...'`, which is now executed by `system`.

```bash
python3 exploit.py --host <IP> --port 9999 --libc <LIBC>
# 1) leak puts, 2) compute base, 3) write GOT, 4) trigger
```

## Lateral movement

There is no other host. The pivot is from the web server to `r1` and from there to the local binary running as root.

## Privilege escalation

The `1337` binary has a canary-protected stack overflow. Leak the canary and PIE base, then build a ROP chain with `pop rdi; ret` to `/bin/sh` and `system`. Connecting to the local port yields a root shell.

```bash
python3 r1.py --host 127.0.0.1 --port 1337
# leak canary + PIE, then ROP: pop rdi; /bin/sh; system
```

## Evidence

- `/etc/passwd` read through `//`.
- `puts` GOT overwritten and command executed.
- Leaked canary/PIE and a root shell through `1337`.

## Lessons learned

- Passing user input to `printf` as a format is a critical bug.
- Arbitrary GOT write turns a leak into execution.
- Local privileged services are part of the escalation surface.

## Mitigation and detection

- Use `printf("%s", input)` and compile with `-Wformat-security`.
- Enable full RELRO, PIE and NX on every binary.
- Do not run local network services as root; use dedicated users.

## References

- [0xdf — Rope](https://0xdf.gitlab.io/2020/05/23/htb-rope.html)
- [IppSec — Rope](https://www.youtube.com/watch?v=GTQxZlr5yvE)
- [Hack The Box — Rope](https://app.hackthebox.com/machines/rope)
