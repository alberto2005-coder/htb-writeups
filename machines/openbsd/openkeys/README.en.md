---
machine: OpenKeyS
os: OpenBSD
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [openbsd, authentication-bypass, cve-2019-19521, xlock, skey]
---

# OpenKeyS — Hack The Box (OpenBSD)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A Vim `.swp` file reveals how login calls `auth_userokay`. The `-schallenge` option (CVE-2019-19521) logs in as `jennifer` and retrieves her SSH key. Then `xlock` with the `auth` group (CVE-2019-19520) writes `/etc/skey/root` and abuses S/Key (CVE-2019-19522) for root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp  ssh   OpenSSH 8.1
80/tcp  http  OpenBSD httpd
```

## Enumeration

- The site is a login portal on the `openkeys.htb` vhost.
- Directory enumeration finds a Vim `.swp` file and the `check_auth` binary.
- `strings` shows `auth_userokay` and the `ld.so` path.
- The session PHP uses `$_REQUEST` and stores the username.

## Foothold

The `.swp` contains the code that passes the username to `auth_userokay`. If the name starts with `-s`, the function interprets the `-schallenge` option and returns success without validating the password (CVE-2019-19521).

The session takes the name from `$_REQUEST`; send `username=-schallenge` to authenticate, then set `username=jennifer` to reach her profile and SSH key.

```bash
curl -c cookies.txt -d 'username=-schallenge&password=x' http://openkeys.htb/
curl -b cookies.txt -d 'username=jennifer' http://openkeys.htb/
```

## Lateral movement

Jennifer's key provides SSH access. Local enumeration confirms OpenBSD 6.6 and the `wheel` group; the target is the `auth` group, which controls `/etc/skey`.

```bash
chmod 600 jennifer.key
ssh -i jennifer.key jennifer@openkeys.htb
```

## Privilege escalation

`/usr/X11R6/bin/xlock` is SGID `auth`. CVE-2019-19520 preserves that group when running a shell through a library loaded from a controlled path.

With the `auth` group, `/etc/skey/root` is written with a known S/Key record and `0600` permissions. `su` with S/Key authentication (CVE-2019-19522) then yields root.

```bash
ls -l /usr/X11R6/bin/xlock
echo 'root md5 0100 <SEED> <HASH>' > /etc/skey/root
chmod 0600 /etc/skey/root
su -a skey root
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- A Vim swap file can reveal internal logic.
- Passing user input to an option-parsing function is dangerous.
- SGID on a graphical tool can preserve privileged groups.
- S/Key with files writable by `auth` is a direct path to root.

## Mitigations and detection

- Patch OpenBSD and reject usernames beginning with `-`.
- Audit SGID binaries and remove unnecessary ones.
- Restrict writes to `/etc/skey` to the real root user.
- Monitor `xlock` executions and changes under `/etc/skey`.

## References

- [0xdf — OpenKeyS](https://0xdf.gitlab.io/2020/12/12/htb-openkeys.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+openkeys)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+openkeys+writeup)
