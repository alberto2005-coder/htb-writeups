---
machine: Travel
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, git, ssrf, memcached, php-deserialization, ldap]
---

# Travel — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An exposed `.git` repository reveals an RSS application. SSRF poisons memcached with a serialized PHP object and yields a container webshell. The database hash is cracked and gives a host user who administers LDAP; changing credentials, SSH key and sudo group reaches root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443 <IP>
git-dumper http://blog.travel.htb/.git/ repo
grep -R "memcache\|unserialize\|rss" repo
# SSRF to memcached
curl -s "http://blog.travel.htb/import?url=http://127.0.0.1:11211/"
# Container webshell
curl -s http://blog.travel.htb/cache.php?cmd=id
# Hash and LDAP
john hash.txt --wordlist=/usr/share/wordlists/rockyou.txt
ldapmodify -x -D "cn=admin,dc=travel,dc=htb" -w '<PASS>' -f change.ldif
```

## Enumeration

- `.git` accessible on the blog vhost.
- RSS application with SSRF and internal memcached.
- Database with hashes and LDAP administered by a host user.

## Initial access

Rebuild the repository with `git-dumper` and review the code: the RSS importer accepts URLs and uses memcached. Send a URL pointing to memcached and write a key with a serialized PHP object the application deserializes, yielding a container webshell.

## Privilege escalation

The container exposes a database with hashes; crack one and obtain SSH to the host. That user administers LDAP: change a privileged user password, add an SSH key and include them in `sudo`, then log in as root.

## Evidence

- Repository rebuilt from `.git`.
- Memcached key and container webshell.
- Cracked hash, LDAP changes and root shell.

## Lessons learned

- An exposed `.git` delivers code and secrets.
- SSRF to memcached can inject serialized objects.
- Poorly delegated LDAP allows identity and privilege changes.

## Mitigation and detection

- Do not publish `.git` and review deployments.
- Isolate memcached and never deserialize cache data.
- Limit LDAP administration and audit group changes.

## References

- [0xdf — Travel](https://0xdf.gitlab.io/2020/09/12/htb-travel.html)
- [Memcached — Protocol](https://github.com/memcached/memcached/blob/master/doc/protocol.txt)
- [Hack The Box — Travel](https://app.hackthebox.com/machines/travel)
