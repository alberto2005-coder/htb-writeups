---
topic: proc
platform: Linux
tags: [linux, credentials, proc, race-condition]
---

# Credential capture via `/proc`

**English** | [🇪🇸 Español](proc-credential-capture.md)

> Reusable note. Aimed at scripts invoked with passwords on the command line, or passing them through environment variables.

## Why it works

A process's arguments (`/proc/<pid>/cmdline`) and environment (`/proc/<pid>/environ`) are readable by its owner and by root. If a maintenance script runs `mysql -u app -p'Secret123'` or `curl -H "Authorization: Bearer ..."`, the credential is there for as long as the process lives. Under a timer that lifetime is milliseconds, so this is a **race**.

## The easy look

```bash
tr '\0' ' ' < /proc/self/cmdline; echo
cat /proc/self/environ | tr '\0' '\n'
ps -eo pid,user,args --sort=start_time | tail -20
```

## Catching an ephemeral process

Aggressive loop (enough when the timer fires once a minute):

```bash
while true; do
  for p in /proc/[0-9]*; do
    c=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null)
    case "$c" in
      *mysql*|*psql*|*redis-cli*|*curl*|*ssh*) echo "$(date +%T) ${p#/proc/}: $c" ;;
    esac
  done
done | tee /tmp/capture.log
```

Variants:

```bash
# just the password, when the pattern is known
watch -n 0.2 "ps -eo args | grep -oP '(?<=-p)[^ ]+' | sort -u"

# with pspy (cron/timers without root)
./pspy64 -pf -i 100
```

Tools that already do this well: `pspy`, `procmon` for Linux (eBPF) and, with root, `auditd` with an `execve` rule.

## What to look for

- Passwords in `-p`, `--password`, `-u user:pass` (Mongo), tokens in `-H "Authorization:"`.
- `environ` containing `DB_PASS`, `API_KEY`, `AWS_*`.
- Open descriptors: `ls -l /proc/<pid>/fd` may show files holding credentials.
- The script itself (`/proc/<pid>/cmdline` gives its path): read it if you can.

## Turning it into access

```bash
mysql -h 127.0.0.1 -u app -p'<PASS>'
ssh <user>@<host>          # reuse
su <user>                  # if it is a local account
```

## Mitigation

- Never pass secrets in `argv`: use environment variables read by the process, `--defaults-extra-file` (MySQL), `.pgpass`, `~/.my.cnf` with mode 600, or a secrets manager.
- `hidepid=2` on `/proc` (`mount -o remount,hidepid=2 /proc`) so each user only sees their own processes.
- Single-use credentials and rotation.

## Detection

- Processes repeatedly reading `/proc/*/cmdline`.
- CPU spikes with constant `/proc` reads and new processes with no binary on disk.

## References

- <https://man7.org/linux/man-pages/man5/proc.5.html>
- <https://github.com/DominicBreuker/pspy>
