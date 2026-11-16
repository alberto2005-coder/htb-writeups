---
machine: Download
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, nodejs, prisma, file-read, postgresql, tty, tiocsti, privesc]
---

# Download — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`/files/download/<id>` is vulnerable to path traversal when the slash is encoded as `%2f`. Reading `app.js` reveals the session cookie signing key and the Prisma model. A login endpoint compares the password's SHA-1 with `startsWith`, which leaks the hash character by character and allows cracking; SSH as `wesley` leads to PostgreSQL. Writing to `postgres`'s `.profile` and using TTY pushback (TIOCSTI) injects commands into root's shell.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH and `80` nginx in front of a Node/Express application.
- The application uploads, views and downloads files.
- `feroxbuster` finds no hidden routes: full IDs are required.

## Enumeration

The `download_session` cookie is base64 plus an HMAC-SHA1 signature. Appending `%2f` to the download ID reads `/etc/passwd`, and walking up directories yields `package.json`, `app.js` and the rest of the code. `app.js` contains the `cookie-session` secret and the Prisma schema.

## Foothold

Login compares `hash.startsWith(input)` against the password's SHA-1, acting as a prefix oracle. Script the extraction of `wesley`'s hash and crack it with `hashcat -m 0`. The password works over SSH.

```bash
curl --path-as-is 'http://<IP>/files/download/..%2f..%2f..%2fetc%2fpasswd'
hashcat -m 0 wesley.hash rockyou.txt
```

## Lateral movement

`/etc/systemd/system/download-site.service` holds `DATABASE_URL` with the PostgreSQL password. The `download` database and `User` table confirm the recovered hash. There are no other local users.

## Privilege escalation

A management script runs as root, executes `su -l postgres` and returns to an interactive shell. Since `postgres` can write its own `.profile`, `COPY ... TO` plants a payload that calls `TIOCSTI` on the parent TTY. When `su` exits, root runs whatever is left in the input buffer.

```sql
COPY (SELECT 'python3 -c "import fcntl,termios; ..."') TO '/var/lib/postgresql/.profile';
```

The payload queues `cp /bin/bash /tmp/root; chmod 6777 /tmp/root`, then `/tmp/root -p` is run.

## Evidence

- `app.js` read through `%2f`.
- Hash extraction through `startsWith`.
- `DATABASE_URL` in the systemd unit.
- Modified `.profile` and a UID 0 shell.

## Lessons learned

- Decoding the URL before validating paths changes the outcome completely.
- Prefix hash comparisons leak the full value.
- Session secrets in code allow cookie forgery.
- Interactive `su` plus TTY pushback turns a write as `postgres` into root.

## Mitigation and detection

- Resolve and canonicalise the path, then verify it stays inside the upload directory.
- Compare hashes in constant time and over the full value.
- Move secrets out of code and rotate `DATABASE_URL`.
- Restrict writes to service homes and disable `TIOCSTI` (`dev.tty.legacy_tiocsti=0`).

## References

- [0xdf — Download](https://0xdf.gitlab.io/2023/11/11/htb-download.html)
- [IppSec — Download](https://www.youtube.com/watch?v=UUn9x7mw1i0)
- [Hack The Box — Download](https://app.hackthebox.com/machines/download)
