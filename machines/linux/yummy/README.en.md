---
machine: Yummy
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, jwt, rsa, sqli, mercurial, rsync]
---

# Yummy — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Calendar export concatenates the filename and allows directory traversal to read source and cron files. The JWT cookie is RSA-signed and the public key allows recovering the private key; the admin token opens the panel. SQLi writes a script into a cron directory, yielding `www-data`; a Mercurial repository leaks credentials and a hook pivots to `dev`, who runs `rsync` as root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 24.04 and `80/tcp` Caddy serving `yummy.htb`.
- The site supports registration, table booking and `.ics` export.
- The session JWT uses RSA and `kid` points to a public key.

## Enumeration

- `/export/../../../../etc/passwd` returns files; repeat the traversal to read source and `/etc/crontab`.
- The repository includes the JWT RSA public key and a database password.
- `RsaCtfTool` recovers the private key and signs an admin token.

## Foothold

Sign a JWT with the admin role and access the panel. Panel SQLi allows `INTO OUTFILE` into a directory executed by cron; write a script that starts a reverse shell.

```bash
python3 jwt_tool.py -T <TOKEN> -S hs256 -p <KEY>
# or sign with the recovered RSA key
# in the panel: SQLi -> SELECT ... INTO OUTFILE '/opt/.../script.sh'
```

## Lateral movement

The shell is `www-data`. The system has a Mercurial repository with `qa` credentials in old commits; `qa` can write a Mercurial hook that runs on `pull` or `commit`.

## Privilege escalation

The Mercurial hook runs code as `dev`. `dev` can run `rsync` as root; use `-e` to launch a shell or write to a privileged destination.

```bash
sudo -l
sudo rsync -e 'sh -c "sh 0<&2 1>&2"' <SRC> <DST>
```

## Evidence

- Traversal in `/export` and source/cron files read.
- Signed admin JWT and SQLi with file write.
- `qa` credentials, Mercurial hook and `rsync` as root.

## Lessons learned

- Path concatenation in exports enables traversal.
- A weak RSA public key can be enough to recover the private key.
- Mercurial hooks and `rsync` with `-e` are execution vectors.

## Mitigation and detection

- Normalize paths and use identifiers instead of filenames.
- Rotate JWT keys and use symmetric algorithms with strong secrets.
- Review Mercurial hooks and restrict privileged `rsync`.

## References

- [0xdf — Yummy](https://0xdf.gitlab.io/2025/02/22/htb-yummy.html)
- [IppSec — Yummy](https://www.youtube.com/watch?v=w6nYrsKsYBQ)
- [Hack The Box — Yummy](https://app.hackthebox.com/machines/yummy)
