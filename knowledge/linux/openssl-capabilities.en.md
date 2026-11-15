---
topic: OpenSSL — binary with capabilities
tags: [linux, openssl, capabilities, cap-setuid, privesc]
---

# OpenSSL — binary with capabilities

**English** | [🌐 Español](openssl-capabilities.md)

## Concept

An OpenSSL copy with capabilities keeps privileges even without SUID. If it has `cap_setuid` or `cap_setgid`, an engine or library calling `setuid(0)` can execute a shell. The copy often exists so a non-root service can use ports or keys, but it opens a direct path to root.

## When it applies

- `getcap -r /` shows an OpenSSL copy with capabilities.
- The binary accepts `-engine` or environment variables such as `OPENSSL_CONF`.
- The user can read or execute the copy.

## Procedure

1. Enumerate capabilities and locate the copy.
2. Review the version and engine loading options.
3. Build a library calling `setuid(0)` and `execve`.
4. Run OpenSSL with the library and obtain root.

## Commands

```bash
getcap -r / 2>/dev/null
/usr/local/bin/openssl version
/usr/local/bin/openssl engine -t -c
gcc -shared -fPIC -o evil.so evil.c
/usr/local/bin/openssl req -engine ./evil.so -new -keyout /dev/null
```

## Variants

- Use `OPENSSL_CONF` to load an engine from a controlled path.
- Abuse `cap_dac_read_search` to read keys.
- Copy the binary and preserve capabilities if the system allows it.

## Limitations

- The capability must include `cap_setuid`.
- OpenSSL may disable engine loading in its config.
- The system may block `execve` from the engine.

## Mitigation

- Remove capabilities from utility copies.
- Use `AmbientCapabilities` only for specific services.
- Audit `getcap -r /` regularly.

## Detection

- Binaries with capabilities outside standard paths.
- OpenSSL loading engines from user directories.
- UID 0 processes spawned by a service.

## References

- [Linux — capabilities(7)](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [0xdf — Lightweight](https://0xdf.gitlab.io/2019/05/11/htb-lightweight.html)
- [CWE-269 — Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
