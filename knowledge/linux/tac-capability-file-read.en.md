---
topic: Linux — `tac` with `cap_dac_read_search` and root file read
tags: [linux, capabilities, cap-dac-read-search, tac, privesc, waldo]
---

# Linux — `tac` with `cap_dac_read_search` and root file read

[🌐 Español](tac-capability-file-read.md) | **English**

## Concept

`cap_dac_read_search` bypasses file read and directory search checks (DAC). A binary such as `tac` carrying that capability can read any file, including `/root/root.txt`, without setuid and without being root. It is a read escalation, not a write one: it gives no shell, but exfiltrates secrets and flags.

On Waldo, `tac` and `logMonitor` had `cap_dac_read_search+ei`; `tac /root/root.txt` revealed the flag.

## When it applies

- `getcap -r /` shows capabilities on unexpected binaries.
- The capability is `cap_dac_read_search` or `cap_dac_override`.
- The binary reads an arbitrary file (`tac`, `cat`, `less`, `head`).
- The target is a flag, a key or a root configuration file.
- On Waldo, user `monitor` had `tac` with the capability.

## Procedure

1. Enumerate capabilities with `getcap -r / 2>/dev/null`.
2. Find a binary that reads files and accepts a path.
3. Read the target directly.
4. If line order matters, run `tac` twice.
5. Look for other sensitive files (`/etc/shadow`, SSH keys, configs).

## Commands

```bash
getcap -r / 2>/dev/null
tac /root/root.txt
tac /root/root.txt | tac
```

```bash
# enumerate other targets
tac /etc/shadow 2>/dev/null | head
tac /root/.ssh/id_rsa 2>/dev/null
```

## Variants

- `cap_dac_override` also allows writing and changing permissions.
- `cap_dac_read_search` on `tar`, `cp` or `rsync` copies the file.
- `logMonitor` or a custom binary with the capability can read root logs.
- Combine with `LD_PRELOAD` if the binary keeps the capability and runs another program.

## Limitations

- Without `cap_dac_read_search` or `cap_dac_override` the file cannot be read.
- The capability must be on the binary, not just the package.
- Containers may drop the capability from the bounding set.
- It grants no write access and no root shell.

## Mitigation

- Audit capabilities with `getcap -r /` and remove them from generic binaries.
- Prefer `setcap` only on binaries that validate path and user.
- Apply `NoNewPrivs` and a minimal bounding set to services.
- Monitor `tac`, `cat` or `tar` execution against `/root`.

## Detection

- `getcap` and `capsh --print` on the host.
- `tac` runs with root paths.
- Reads of `/etc/shadow` or SSH keys by non-root users.
- Capabilities added to binaries outside deployment.

## References

- [Linux capabilities](https://man7.org/linux/man-pages/man7/capabilities.7.html)
- [capsh](https://man7.org/linux/man-pages/man1/capsh.1.html)
- [0xdf — Waldo](https://0xdf.gitlab.io/2018/12/15/htb-waldo.html)
- [Waldo writeup](../../machines/linux/waldo/README.en.md)
