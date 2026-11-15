---
topic: safeapache2ctl — privileged wrapper bypass
tags: [linux, apache, wrapper, loadmodule, include, privesc]
---

# safeapache2ctl — privileged wrapper bypass

[🇪🇸 Español](safeapache2ctl-bypass.md) | **English**

## Concept

A wrapper such as `safeapache2ctl` validates configuration before starting Apache as root. If it accepts a user-controlled `-f` configuration, `Include` reads root files and `LoadModule` loads a user `.so` before Apache fails, leaving privileged execution.

## When it applies

- A privileged script or binary calls `apache2ctl`.
- The wrapper only validates syntax or a specific path.
- The user can pass `-f` with their own configuration.
- `Include` or `LoadModule` runs before the final check.

## Procedure

1. Read the wrapper and locate the check.
2. Check whether it accepts `-f` and runs `Include`/`LoadModule` as root.
3. Include a root file to read its first line or load a `.so`.
4. Run the wrapper and use the SUID binary created by the module.

```bash
printf 'Include /root/root.txt\n' > /home/<USER>/confs/x.conf
safeapache2ctl -f /home/<USER>/confs/x.conf
```

```bash
printf 'LoadModule evil /home/<USER>/confs/evil.so\n' > /home/<USER>/confs/x.conf
safeapache2ctl -f /home/<USER>/confs/x.conf
/tmp/0xdf -p
```

## Variants

- `Include` to read the first line of a root file.
- `LoadModule` with a `.so` that creates a SUID binary.
- `ErrorLog`/`CustomLog` to write to privileged paths.
- `LD_PRELOAD` or `PATH` if the wrapper does not sanitize the environment.

## Limitations

- The wrapper may sanitize the environment.
- The binary may be static or use absolute paths.
- AppArmor/SELinux may block writes.

## Mitigation

- Use absolute paths and clear the environment.
- Validate modules and includes too.
- Run Apache as an unprivileged user.

## Detection

- `-f` configurations in user directories.
- `Include` of files outside the webroot or `/etc/apache2`.
- `.so` modules outside `/usr/lib/apache2` and new SUID binaries.

## References

- [Apache — security tips](https://httpd.apache.org/docs/2.4/misc/security_tips.html)
- [0xdf — Guardian](https://0xdf.gitlab.io/2026/02/28/htb-guardian.html)
- [CWE-426 — Untrusted Search Path](https://cwe.mitre.org/data/definitions/426.html)
