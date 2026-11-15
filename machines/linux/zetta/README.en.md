---
machine: Zetta
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, ftp, rsync, postgres, sqli, privesc]
---

# Zetta — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Pure-FTPd accepts any 32-character username and password; FXP reveals an IPv6 address and rsync on 8730 exposes `/etc`. Read the rsyslog configuration and get `roy`; rsync allows writing his `authorized_keys`. The rsyslog template inserts the message into PostgreSQL, enabling SQLi with stacked queries: write a `postgres` key and read `.psql_history`, which reveals the password scheme and allows `su root`.

## Recon

```bash
nmap -Pn -sCV -p21,22,80,8730 <IP>
```

- `21` Pure-FTPd, `22` SSH, `80` HTTP and `8730` rsync.
- FTP advertises `AUTH TLS` and accepts 32-character usernames.
- Port 8730 answers the rsync module.

## Enumeration

- Any matching 32-character username and password authenticates; the home is `/srv/ftp/home/<USER>`.
- `PRET EPRT`/`PORT` allows FTP bounce; `EPRT` reveals an IPv6 address and an internal rsync service.
- `rsync rsync://<IP>:8730/` lists modules and `/etc` is readable.

## Foothold

Download `/etc/rsyslog.conf` and `/etc/rsyslog.d/*.conf`. The configuration contains `roy` credentials; rsync also allows uploading an `authorized_keys` into `home_roy`. Log in over SSH as `roy`.

```bash
rsync rsync://<IP>:8730/etc/rsyslog.d/ /tmp/rsyslog/
rsync /tmp/authorized_keys rsync://<IP>:8730/home_roy/.ssh/authorized_keys
ssh -i id_rsa roy@<IP>
```

## Lateral movement

The rsyslog configuration uses `ompgsql` with `postgres` and an SQL template. `roy` is in `adm` and can read `/var/log/postgresql`, so test injection with `logger`.

```bash
logger -p local7.info "test', null)-- -"
```

## Privilege escalation

The injection accepts stacked queries. Create a table, insert a public key and write it to `/var/lib/postgresql/.ssh/authorized_keys` with `COPY ... TO`. Then read `.psql_history`, which contains a PostgreSQL password; the scheme appends `@root` for `su`, yielding root.

```bash
logger -p local7.info "sd',null); CREATE TABLE aaa (c text); INSERT INTO aaa VALUES (\\$$<PUBKEY>\\$$); COPY (SELECT * FROM aaa) TO \\$$/var/lib/postgresql/.ssh/authorized_keys\\$$;-- -"
```

## Evidence

- FTP with 32-character authentication and EPRT bounce.
- rsync on 8730 with readable `/etc` and writable `home_roy`.
- rsyslog template and SQLi through `logger`.
- `COPY TO` writing the `postgres` key and `su root`.

## Lessons learned

- An FTP server with weak authentication can pivot to IPv6.
- Unrestricted rsync reads configuration and writes keys.
- A log SQL template is a direct database entry point.

## Mitigation and detection

- Require real authentication and disable FXP.
- Restrict rsync modules and write permissions.
- Parameterize the rsyslog template and limit `COPY ... PROGRAM`.

## References

- [0xdf — Zetta](https://0xdf.gitlab.io/2020/02/22/htb-zetta.html)
- [IppSec — Zetta](https://www.youtube.com/watch?v=8XmTz3A5rUo)
- [Hack The Box — Zetta](https://app.hackthebox.com/machines/zetta)
