---
machine: Encoding
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, file-read, git, ssrf, php-filter, git-hooks, systemd, privesc]
---

# Encoding — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The main site has a file read that downloads the `.git` repository of a vhost that is not directly reachable. The code reveals the `api.haxtables.htb` vhost and a local file inclusion; an SSRF reaches that inclusion and a PHP filter chain (`php://filter`) turns the read into RCE as `www-data`. `www-data` can run `git-commit.sh` as `svc`; the `.git` directory is writable, so a `post-commit` hook adds an SSH key for `svc`. `svc` can restart services with `systemctl` as root and `/etc/systemd/system` is writable through an ACL: a unit is modified to run a shell and restarted.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH 8.9p1 Ubuntu.
- `80`: Apache httpd 2.4.52.

```bash
echo '<IP> haxtables.htb image.haxtables.htb api.haxtables.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://haxtables.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

The main site is a tools page. The `image.haxtables.htb` vhost exposes a utility that takes a URL or filename and returns content. Relative paths confirm a file read; it downloads the `.git` repository of `api.haxtables.htb`, which does not answer directly from outside.

The repository contains the API code: routes, parameters and a call that includes files. It also reveals `git-commit.sh` and the service configuration.

## Foothold

The API exposes a local file inclusion in a template parameter. The SSRF from the image site reaches that route from localhost, and the inclusion becomes execution by chaining PHP filters:

```text
php://filter/convert.iconv.../resource=<PAYLOAD>
```

The result is a webshell or a reverse shell as `www-data`.

## Lateral movement

`www-data` can run the commit script as another user:

```text
(svc) NOPASSWD: /var/www/image/scripts/git-commit.sh
```

`/var/www/image/.git` has an ACL granting write access to `www-data`. A `.git/hooks/post-commit` script with a public SSH key is created and a commit is triggered through `git-commit.sh`; the hook runs as `svc` and adds the key to its `authorized_keys`. The hook contains:

```bash
#!/bin/bash
mkdir -p /home/svc/.ssh
echo '<PUBLIC_KEY>' >> /home/svc/.ssh/authorized_keys
chmod 600 /home/svc/.ssh/authorized_keys
```

## Privilege escalation

`svc` can restart any service as root:

```text
(root) NOPASSWD: /usr/bin/systemctl restart *
```

`/etc/systemd/system` is writable by `svc` through an ACL. A unit is copied or modified so `ExecStart` runs a shell or copies `bash` with setuid, the daemon is reloaded and the service restarted. The resulting process runs as root.

```bash
systemctl daemon-reload
sudo systemctl restart <SERVICE>
```

## Evidence

- File read on `image.haxtables.htb` and download of the API `.git`.
- SSRF to the local inclusion and `id` execution as `www-data`.
- Writable `.git` ACL and `post-commit` hook executed as `svc`.
- `sudo -l` with `systemctl restart *`.
- Writable `/etc/systemd/system` ACL and modified unit.
- `id` with UID 0 after restarting the service.

## Lessons learned

- A file read can expose a full Git repository even when the vhost is unreachable.
- PHP filters turn an LFI into RCE without uploading a file.
- An SSRF can reach services bound to localhost only.
- Git hooks run as the user performing the commit.
- `sudo systemctl restart *` over writable units is direct root.

## Mitigations and detection

- Do not allow arbitrary paths in image or download utilities; use allowlists.
- Block `php://filter` and validate schemes and paths in inclusions.
- Restrict SSRF with destination allowlists and no localhost access.
- Protect `.git` and its hooks; do not grant write access to the web user.
- Avoid `sudo systemctl restart *`; allow only specific, non-writable units.
- Alert on automated commits, new hooks and service restarts outside maintenance.

## References

- [0xdf — Encoding](https://0xdf.gitlab.io/2023/04/15/htb-encoding.html)
- [IppSec — Encoding](https://www.youtube.com/watch?v=iyGvnmkx1es)
- [Hack The Box — Encoding](https://app.hackthebox.com/machines/encoding)
- [Knowledge — Privilege escalation with Git hooks](../../../knowledge/linux/git-hooks-privesc.en.md)
