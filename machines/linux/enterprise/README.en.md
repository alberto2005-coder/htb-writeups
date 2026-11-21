---
machine: Enterprise
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, wordpress, joomla, docker, sqli, webshell, buffer-overflow, ret2libc, privesc]
---

# Enterprise — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

WordPress 4.8.1 runs the `lcars` plugin, whose `lcars_db.php?query=` is injectable. Dumping `wp_posts` recovers passwords from a draft and gives access to WordPress and, through reuse, to the Joomla panel on `8080`. A PHP template is edited in both containers to gain execution. The Joomla container mounts a host directory, so a webshell there gives a shell on the real machine. On the host, `xinetd` publishes `/bin/lcars` on `32812`; after the access code, option 4 copies input into a 212-byte buffer without bounds checks and allows a `ret2libc` to `system("/bin/sh")` as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443,8080,32812 <IP>
```

- `22`: OpenSSH 7.4p1 Ubuntu.
- `80`: Apache with WordPress 4.8.1.
- `443`: default Apache page.
- `8080`: Joomla.
- `32812`: LCARS service under `xinetd`.

```bash
echo '<IP> enterprise.htb' | sudo tee -a /etc/hosts
wpscan --url http://enterprise.htb --enumerate ap,us
```

## Enumeration

`wpscan` identifies the `lcars` plugin. Its `lcars_db.php` passes the `query` parameter straight to MySQL and is vulnerable to error-based injection:

```bash
sqlmap -u 'http://enterprise.htb/wp-content/plugins/lcars/lcars_db.php?query=1' --batch --dbs
sqlmap -u 'http://enterprise.htb/wp-content/plugins/lcars/lcars_db.php?query=1' -D wordpress -T wp_posts --dump
```

The `wp_posts` dump includes a draft with several passwords and usernames. `william.riker` logs into WordPress; `geordi.la.forge` and `Guinan` are Joomla accounts, and `geordi.la.forge` reuses a draft password and has Super User rights.

## Foothold

In WordPress, **Appearance → Themes → Editor** allows editing a template. Add a PHP webshell and visit a post with the parameter the webshell expects.

The result is a shell as `www-data` in a container whose hostname is a Docker ID.

In Joomla, `/administrator` accepts `geordi.la.forge` credentials. **Extensions → Templates → Templates** allows editing a template; insert the same webshell and visit a non-existent path with the parameter it expects.

## Lateral movement

The Joomla container mounts a host directory, `/var/www/html/files`. A PHP file written from the container appears on the host and runs from the main site:

`http://enterprise.htb/files/shell.php`

That gives a shell as `www-data` on the `enterprise` host, outside Docker.

## Privilege escalation

`ps`/`pstree` shows `xinetd` launching `/bin/lcars` on connect to `32812`. The binary asks for an access code (`picarda1`), shows a menu, and option 4 requests a "Security Override" copied into a 212-byte buffer.

With the binary and the system libc, compute the offsets and build a `ret2libc`:

```python
from pwn import *
system = p32(<SYSTEM>)
exit_ = p32(<EXIT>)
sh = p32(<BINSH>)
payload = b"A" * 212 + system + exit_ + sh
```

```text
Enter Bridge Access Code: picarda1
Waiting for input: 4
Enter Security Override: <payload>
```

Returning into `system("/bin/sh")` gives a root shell.

## Evidence

- Injectable `lcars_db.php?query=` and a `wp_posts` dump with credentials.
- WordPress and Joomla access with draft accounts.
- Edited templates and webshells in both containers.
- Mounted directory and a shell on the `enterprise` host.
- `/bin/lcars` under `xinetd`, option 4 and a `ret2libc` root shell.

## Lessons learned

- A plugin with SQLi exposes the whole database, including drafts.
- Password reuse links WordPress and Joomla.
- The template editor is code execution once an administrator is compromised.
- A shared volume between container and host breaks isolation.
- Old `xinetd` services can hide vulnerable binaries.
- A fixed-size buffer without a length check allows return-address control.

## Mitigations and detection

- Update WordPress, plugins and Joomla; remove unsupported components.
- Parameterize queries and review custom plugins.
- Restrict the template editor and enforce MFA for administrators.
- Do not mount host directories into web containers; use minimal volumes.
- Build with `-fstack-protector`, ASLR and `NX`, and review legacy services.
- Monitor writes to the mounted directory and executions of `/bin/lcars`.

## References

- [0xdf — Enterprise](https://0xdf.gitlab.io/2021/06/16/htb-enterprise.html)
- [Hack The Box — Enterprise](https://app.hackthebox.com/machines/enterprise)
