---
machine: CrossFitTwo
os: OpenBSD
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [openbsd, sqli, nodejs, yubikey, changelist]
---

# CrossFitTwo — Hack The Box (OpenBSD)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The employee site uses a WebSocket with SQLi; a Flask proxy reads files and credentials. An Express vhost loads modules from a writable directory, allowing code execution as another user. The SUID `log` binary reads `changelist` backups containing root's SSH key and Yubikey material; both factors open SSH as root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp  ssh
80/tcp  http   nginx / relayd
5000/tcp http  Express (interno)
9999/tcp http  relayd (interno)
```

## Enumeration

- `employees.crossfit.htb` and `crossfit-club.htb` are different vhosts.
- The employee WebSocket reflects SQL queries and allows UNION.
- A local Flask proxy makes `sqlmap` usable against the WebSocket.
- File reads reveal credentials and application paths.

## Foothold

The injection is confirmed with a boolean query and automated with `sqlmap` through the proxy. The database yields `david` credentials and SSH access.

```bash
sqlmap -r ws.request --technique=U --batch --timeout 3 --ignore-timeouts
ssh david@crossfit.htb
```

## Lateral movement

`david` belongs to `sysadmins`, which can write to `/opt/sysadmin`. The `crossfit-club.htb` vhost runs Express and a cron deletes `/opt/sysadmin/node_modules` every five minutes.

Before deletion, a malicious `ws` or `log-to-file` module is placed in the search path. When the process restarts, Node loads the controlled module and executes code as `john`.

```bash
find /opt/sysadmin -maxdepth 3 -ls
```

## Privilege escalation

`/usr/local/bin/log` is SUID root and group `staff`. It reads backup files and exposes `/var/backups`, where `changelist` keeps copies of `/root/.ssh/id_rsa` and `/var/db/yubikey/root.*`.

Root's private key is extracted and Yubikey codes are generated from the key, UID and counter. `sshd` requires both key and password authentication, so the key and OTP are used as two factors.

```bash
log /var/backups/root_.ssh_id_rsa.current
log /var/backups/var_db_yubikey_root.key.current
ssh -i root.key root@crossfit.htb
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- A WebSocket can be as injectable as an HTTP form.
- Node module resolution from writable directories is RCE.
- `changelist` backups can retain keys and authentication secrets.
- MFA fails when both factors live on the same host.

## Mitigations and detection

- Parameterise queries and validate the WebSocket origin.
- Mount `/opt/sysadmin` read-only and pin `NODE_PATH`.
- Protect `/var/backups` and exclude private keys from `changelist`.
- Store Yubikey secrets off-host and rotate them.

## References

- [0xdf — CrossFitTwo](https://0xdf.gitlab.io/2021/08/14/htb-crossfittwo.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+crossfittwo)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+crossfittwo+writeup)
