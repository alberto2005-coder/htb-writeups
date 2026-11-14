---
machine: Unbalanced
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, encfs, squid, xpath, pihole]
---

# Unbalanced — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`rsync` exposes an EncFS-encrypted backup. The password is cracked, the filesystem mounted, and Squid configuration plus credentials appear. The proxy reveals internal hosts; one runs an intranet with XPath injection that leaks users and passwords. SSH gives `bryan`, pivots to the Pi-hole container, and a script with root credentials closes the chain.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp    ssh
873/tcp   rsync
3128/tcp  squid
```

## Enumeration

- `rsync --list-only rsync://<IP>` shows the `conf_backups` module.
- The module contains `.encfs6.xml` and files with encrypted names.
- `encfs2john` and `john` recover the EncFS password.
- `squid.conf` reveals `intranet.unbalanced.htb` and two internal hosts.

## Foothold

The backup is downloaded, EncFS is cracked and mounted. Squid configuration allows using the proxy and enumerating the cache, which reveals `172.31.179.2` and `172.31.179.3`.

The intranet login is vulnerable to XPath injection. A boolean condition extracts users and passwords; one provides SSH as `bryan`.

```bash
rsync -a rsync://<IP>/conf_backups/ backup/
encfs2john backup/ > encfs.hash
john --wordlist=/usr/share/wordlists/rockyou.txt encfs.hash
encfs backup/ /mnt/decrypted
```

## Lateral movement

As `bryan`, `ss` shows two local ports: 8080 and 5553. Port 8080 is the Pi-hole panel in a container. It is forwarded over SSH and the panel is exploited to upload a webshell.

A maintenance script inside the container contains the host root password.

```bash
ssh -L 8080:127.0.0.1:8080 bryan@<IP>
```

## Privilege escalation

The password found in the script is used with `su` or SSH as root. The container shares a secret that is also valid on the host.

```bash
su -
id
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- A configuration backup can contain the key to its own encryption.
- EncFS with a weak password does not protect data.
- Unauthenticated Squid exposes the internal topology.
- XPath injection can dump complete credentials.
- Containers must not share passwords with the host.

## Mitigations and detection

- Restrict `rsync` and keep `.encfs6.xml` out of the backup.
- Use strong passwords and keys stored outside the backup.
- Require Squid authentication and restrict ACLs.
- Parameterise XPath and separate credentials per service.

## References

- [0xdf — Unbalanced](https://0xdf.gitlab.io/2020/12/05/htb-unbalanced.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+unbalanced)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+unbalanced+writeup)
