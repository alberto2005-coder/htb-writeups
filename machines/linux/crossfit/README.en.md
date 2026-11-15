---
machine: CrossFit
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, xss, csrf, ftp, ansible, php-shellcommand, cron, privesc]
---

# CrossFit — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

XSS in the user-agent reaches the admin bot; CORS reveals an FTP subdomain and CSRF creates an account. FTP uploads a webshell and gives `www-data`. An Ansible hash cracks to `hank`, and a `php-shellcommand` plugin injects commands for `isaac`. A cron binary with arbitrary write and a predictable symlink writes root's `authorized_keys`.

## Recon

```bash
nmap -Pn -sCV -p21,22,80 <IP>
```

- `21` FTP, `22` SSH and `80` Apache with `crossfit.htb`.
- `wfuzz` finds `ftp.crossfit.htb` and `admin.crossfit.htb`.
- The main site has a report form that records the user-agent.

## Enumeration

- An XSS payload in the user-agent runs in the administrator's browser.
- From there it requests `ftp.crossfit.htb`; CORS allows reading the response.
- The CSRF token is extracted and a cross-site request creates an FTP account.

## Foothold

The FTP account uploads a PHP webshell into the served directory. Visiting it gives `www-data`.

```bash
curl 'http://crossfit.htb/uploads/shell.php?cmd=id'
```

## Lateral movement

`/etc/ansible/playbooks/adduser_hank.yml` holds `hank`'s hash. Crack it with Hashcat and use it for `su hank`; `hank` is in `admins`, which allows reading `isaac`'s `send_updates` directory.

```bash
hashcat -m 1800 hank.hash rockyou.txt
su hank
```

The `send_updates` `php-shellcommand` plugin concatenates a parameter into a system call. Inject a command from the database and get `isaac`.

## Privilege escalation

A cron runs `/bin/dbmsg` as root. The binary reads messages from MySQL, builds a name in `/var/local` with `rand()` and writes three fields; the name is predictable because the cron runs at a fixed second. Create a symlink with that name to `/root/.ssh/authorized_keys` and insert the public key into the database.

```bash
ln -s /root/.ssh/authorized_keys /var/local/<HASH>
```

## Evidence

- User-agent XSS and admin bot.
- CORS, CSRF and FTP account.
- Webshell and `www-data`.
- Ansible hash and `hank`.
- `php-shellcommand` and `isaac`.
- `dbmsg`, symlink and root.

## Lessons learned

- User-agent is an XSS channel when rendered in a panel.
- Misconfigured CORS exposes internal subdomains.
- Ansible playbooks store reusable hashes.
- A cron with predictable names and symlinks is arbitrary write.

## Mitigation and detection

- Escape the user-agent and use CSP.
- Restrict CORS to explicit origins.
- Keep hashes out of playbooks; use vault.
- Avoid symlinks and predictable names in root scripts.

## References

- [0xdf — CrossFit](https://0xdf.gitlab.io/2021/03/20/htb-crossfit.html)
- [IppSec — CrossFit](https://www.youtube.com/watch?v=Z3Lj_YN0crc)
- [Hack The Box — CrossFit](https://app.hackthebox.com/machines/crossfit)
