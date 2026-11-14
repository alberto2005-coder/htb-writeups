---
machine: Reddish
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, docker, node-red, redis, pivoting, rsync]
---

# Reddish — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Node-RED on 1880 allows a flow with an `exec` node and a shell in its container. Three Docker networks are then crossed: unauthenticated Redis writes a webshell, a wildcard cron yields the `www` user, and a privileged `backup` container mounts the host disk. A host cron closes with root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
1880/tcp  http  Node.js Express / Node-RED
172.19.0.2:6379  redis
172.19.0.4:80    http
172.20.0.2:873   rsync
```

## Enumeration

- `POST /` on 1880 returns an identifier and the `/red/{id}` editor path.
- The editor allows dragging `exec`, `http request` and `function` nodes without authentication.
- The container lacks `curl`, `wget` and `nc`; Perl or an upload flow is used instead.
- Internal scans reveal the `172.19.0.0/16` and `172.20.0.0/16` networks.

## Foothold

A flow with an `exec` node runs a Perl reverse shell. The flow is deployed and the callback arrives as root in the `nodered` container. With no direct host connectivity, `socat` or Meterpreter tunnels reach the internal services.

```text
POST http://<IP>:1880/  ->  {"path":"/red/<ID>"}
```

## Lateral movement

Redis at `172.19.0.2:6379` has no `AUTH`. `dir` and `dbfilename` are changed, a PHP webshell is written and saved with `SAVE`; the site at `172.19.0.4` executes it. The webshell provides a shell as `www-data`.

As `www-data`, a cron runs `rsync` with a wildcard over a writable directory. Filenames are interpreted as `rsync` options; files named `-e` and a helper script execute commands as the cron user.

```bash
redis-cli -h 172.19.0.2
config set dir /var/www/html/<APP_DIR>
config set dbfilename shell.php
save
```

## Privilege escalation

The `backup` container is reachable over `rsync` and runs with `--privileged`. A cron inside the container gives root on `backup`; `/dev/sda1` is then mounted and the host filesystem becomes accessible.

With the host `/etc/cron.d` mounted and writable, a cron running a root script is dropped.

```bash
mount /dev/sda1 /mnt
echo '* * * * * root sh /opt/shell.sh' > /mnt/etc/cron.d/shell
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- An unauthenticated flow editor is direct remote execution.
- Redis without `AUTH` can write files when the process has permissions.
- `rsync` and `tar` wildcards turn filenames into options.
- `--privileged` exposes host devices and breaks isolation.

## Mitigations and detection

- Authenticate Node-RED and restrict dangerous nodes.
- Require `AUTH`, bind Redis to loopback and minimise permissions.
- Avoid wildcards over writable directories and terminate options with `--`.
- Do not run privileged containers or mount the host disk.

## References

- [0xdf — Reddish](https://0xdf.gitlab.io/2019/01/26/htb-reddish.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+reddish)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+reddish+writeup)
