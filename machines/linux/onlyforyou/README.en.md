---
machine: OnlyForYou
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, flask, lfi, command-injection, neo4j, cypher, pip]
---

# OnlyForYou — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `beta` subdomain mishandles path normalization and allows absolute file reads; the main application source reveals command injection in the email validator. After a `www-data` shell, a tunnel to Neo4j enables Cypher injection that leaks `john`'s hash. The user may run `pip3 download` as root, and a malicious package executes `setup.py` with root privileges.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
```

- SSH and Nginx.
- `only4you.htb` and `beta.only4you.htb`.
- `ffuf` and `feroxbuster` find `/download` and form endpoints.

## Enumeration

- `/download` uses `os.path.join` with an insufficient `..` filter.
- An absolute path such as `/etc/passwd` bypasses the filter.
- `form.py` passes the email domain to `subprocess.run(..., shell=True)`.
- Neo4j listens locally and is reached through Chisel.

## Foothold

Read source through the absolute path and inject a command in the email field. `re.match` only anchors the start, so a newline or metacharacter lets `dig` run with extra arguments and returns a reverse shell.

```bash
curl -s "http://beta.only4you.htb/download?file=/var/www/only4you.htb/form.py"
```

## Privilege escalation

Chisel reaches the Neo4j panel. Cypher injection in search dumps users and `john`'s hash, which is cracked. `john` may run `pip3 download` as root; publish a malicious sdist on the local Gogs and download it to execute `setup.py` as root.

```bash
sudo -l
pip3 download --no-deps --no-binary :all: <package>
```

## Evidence

- Read of `/etc/passwd` and `form.py`.
- Injected email request and `www-data` shell.
- Cypher query revealing `john`'s hash.
- `sudo -l` and `setup.py` running as root.

## Lessons learned

- `os.path.join` discards the base when the second argument is absolute.
- `re.match` does not validate the whole string.
- `pip download` from an untrusted package executes code during build.

## Mitigations and detection

- Resolve and confine paths with `Path.resolve()` and an allowed root.
- Parameterize commands and avoid `shell=True`.
- Restrict Neo4j to localhost and require authentication.
- Never run `pip` as root against untrusted indexes.
- References: HTB OnlyForYou, 0xdf, CWE-22/CWE-78.

## References

- <https://www.hackthebox.com/machines/OnlyForYou>
- <https://0xdf.gitlab.io/2023/08/26/htb-onlyforyou.html>
- <https://cwe.mitre.org/data/definitions/78.html>
- <https://attack.mitre.org/techniques/T1059/004/>
