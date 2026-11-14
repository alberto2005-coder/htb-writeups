---
topic: doas — rule review and abuse
tags: [linux, openbsd, doas, privesc, sudo]
---

# doas — rule review and abuse

[🌐 Español](doas-privesc.md) | **English**

## Concept

`doas` runs commands as another user according to `/etc/doas.conf`. Overly broad rules, `nopass`, `setenv` or binaries that allow shell escapes turn a legitimate delegation into root.

## When it applies

- `/etc/doas.conf` with `permit nopass` for a binary.
- Users able to edit the configuration file.
- Commands such as `vim`, `less`, `find`, `ssh-keygen` or `sh`.

## Procedure

1. Read `/etc/doas.conf` and check the version.
2. Run `doas -C /etc/doas.conf` to validate rules.
3. Identify allowed commands and their escape options.
4. Spawn a shell or write a privileged file.
5. Confirm the resulting UID.

## Commands

```bash
cat /etc/doas.conf
doas -C /etc/doas.conf
doas -l
doas <COMMAND>
```

## Variants

- `doas vim` and `:!sh`.
- `doas ssh-keygen` to sign a key.
- A user-writable `doas.conf`.

## Limitations

- The rule may restrict arguments and users.
- `doas` may not be installed.
- The binary must retain an escape path.

## Mitigation

- Limit `doas` to specific commands and arguments.
- Avoid `nopass` and `setenv`.
- Protect `/etc/doas.conf` and audit changes.

## Detection

- `doas` executions from non-interactive processes.
- Shells spawned by delegated binaries and `doas.conf` changes.

## References

- <https://man.openbsd.org/doas.conf>
- <https://attack.mitre.org/techniques/T1548/>
