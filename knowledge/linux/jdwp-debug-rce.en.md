---
topic: JDWP — remote execution through the Java debugger
tags: [linux, java, jdwp, debug, rce, privesc]
---

# JDWP — remote execution through the Java debugger

[🌐 Español](jdwp-debug-rce.md) | **English**

## Concept

JDWP (Java Debug Wire Protocol) is the protocol a JVM uses with `-agentlib:jdwp` to accept a debugger. It has no authentication: anyone who connects can inspect classes, create objects and call `Runtime.exec()` in the process context. If the JVM runs as root, the connection is root.

## When it applies

- `ps` shows `-agentlib:jdwp=transport=dt_socket,server=y,address=...`.
- The port is on `localhost` but SSH, a proxy or SSRF is available.
- The Java process has high privileges.

## Procedure

1. Find the real debug port in the command line (for example, `8000`).
2. Confirm it accepts connections (`nc`, `jdb` or the script).
3. Create a script with the reverse shell on disk.
4. Run `jdwp-shellifier` with `--cmd` pointing at the script.
5. Catch the connection on the listener.

## Commands

```bash
ps auxww | grep -- '-agentlib:jdwp'
ssh -L 223:localhost:8000 user@<IP>
python3 jdwp-shellifier.py -t 127.0.0.1 -p 223 --cmd '/dev/shm/x.sh'
```

`223` is the tunnel's local port; the JVM still listens on `8000`.

## Variants

- Interactive `jdb` with `print new java.io.File(...)`.
- Direct connection when the port is exposed.
- Port reachable through SSRF or a reverse proxy.
- In-memory shell with a Java class instead of a script.

## Limitations

- The debugger must be enabled and listening.
- Some versions require a handshake or suspend the process.
- A firewall may block the port even when it is on `localhost`.
- The script must be executable by the JVM user.

## Mitigation

- Do not enable JDWP in production.
- If debugging is required, use a local socket with ACLs and authenticated tunnels.
- Run the JVM as an unprivileged user.
- Monitor for `jdwp` in process command lines.

## Detection

- Process command lines containing `-agentlib:jdwp`.
- Inbound connections to the debug port.
- Child processes created by the JVM.
- Java reading scripts from `/dev/shm`.

## References

- [Oracle — JPDA](https://docs.oracle.com/javase/8/docs/technotes/guides/jpda/)
- [IOActive — jdwp-shellifier](https://github.com/IOActive/jdwp-shellifier)
- [0xdf — AI](https://0xdf.gitlab.io/2020/01/25/htb-ai.html)
