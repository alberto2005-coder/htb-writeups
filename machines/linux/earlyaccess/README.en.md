---
machine: EarlyAccess
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, xss, sqli, second-order, lfi, docker, password-reuse, capabilities]
---

# EarlyAccess — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Three vhosts share the same IP: `earlyaccess.htb`, `game.earlyaccess.htb` and `dev.earlyaccess.htb`. Registration on the main site does not sanitize the username, so a stored XSS steals the administrator's cookie. That session reaches the game and `validate.py`, the key validator that allows generating a valid key. The key opens the dev site, where a second-order SQLi (the name is stored and used later in a query) dumps hashes that are cracked. The LFI in `hash.php` plus log poisoning yields RCE as `www-data` in the web container. Password reuse leads to `www-adm`, then to `drew` on the host (their `.wgetrc` stores credentials for the key API) and to `game-tester` on the game server. Root there comes from crashing the service; with `game-adm`'s hash a `su` on the host is possible, and a capability on `arp` reads root's key.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443 <IP>
```

- `22` OpenSSH 7.9p1 Debian 10+deb10u2.
- `80` and `443` Apache httpd 2.4.38 (Debian).
- The `443` certificate reveals the `earlyaccess.htb` domain.

```bash
ffuf -u https://earlyaccess.htb -H "Host: FUZZ.earlyaccess.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -fs <SIZE>
```

`game` and `dev` appear. All three are added to `/etc/hosts`.

## Enumeration

The main site has a home page, messaging, a forum, a store, key registration and a profile. Registration accepts usernames with special characters and the profile reflects them unescaped.

Messaging and the forum deliver content to other users; the administrator reviews profiles and messages, so a stored XSS in the username runs in their browser. A local server receives the request carrying the session cookie.

With the admin cookie, private features and the panel that generates game keys are reachable.

## Foothold

`game.earlyaccess.htb` serves `validate.py`, a key validator with the format:

```text
AAAAA-BBBBB-CCCC1-DDDDD-1234
```

The script checks the groups and the final digit, and can be reproduced to generate a valid key. Entering it in the profile grants access to the dev site.

On `dev.earlyaccess.htb` the username is stored at registration and later inserted unparameterized into a query: a second-order SQLi. A UNION dumps the user hashes:

```bash
sqlmap -u "https://dev.earlyaccess.htb/<PATH>" --data="<PARAMS>" --batch --dump
hashcat -m 0 hashes /usr/share/wordlists/rockyou.txt
```

The cracked passwords open the dev panel. `hash.php` includes files based on a parameter, allowing source disclosure and, with log or session poisoning, writing a webshell into the web container:

```bash
curl -s "https://dev.earlyaccess.htb/hash.php?file=../../../../var/log/apache2/access.log"
```

## Lateral movement

The webshell runs as `www-data` inside a Docker container. Enumeration shows the internal network and configuration files with `www-adm` credentials. That password is reused for SSH to the host as `www-adm`.

`drew`'s home contains a `.wgetrc` with credentials for the game key verification API. Querying it returns `drew`'s password, and SSH leads to their account and to `game-tester` on the game server.

## Privilege escalation

On the game server, the binary listens locally and processes games. A malformed value crashes it and leaves a root shell in that container. From there, `game-adm`'s hash on the host is read, cracked and used with `su`.

`game-adm` belongs to the `adm` group, which grants access to logs and the `arp` binary. The binary carries a capability that reads files with elevated rights:

```bash
getcap -r / 2>/dev/null
/usr/sbin/arp -v -f /root/root.txt
cat /root/.ssh/id_rsa
```

Root's private key completes the box.

## Evidence

- Username with XSS and admin cookie received.
- Game key generated from `validate.py`.
- UNION on the dev site and cracked hashes.
- Webshell in the container and `www-adm` credentials.
- `drew`'s `.wgetrc` and the key API queried.
- Game server crash and `su` as `game-adm`.
- `getcap` on `arp` and root's key read.

## Lessons learned

- A stored XSS in a field only the administrator reviews is still an entry point.
- Second-order SQLi does not appear in the request that triggers it.
- An LFI becomes RCE with writable logs or sessions.
- Password reuse chains containers and hosts without exploits.
- Binaries with capabilities are a quiet escalation compared with SUID.

## Mitigations and detection

- Escape and validate every reflected field, including usernames and profiles.
- Parameterize all queries, including those executed in later steps.
- Never include user-supplied paths; use template allowlists.
- Rotate passwords across services and keep them out of `.wgetrc` and repositories.
- Review `getcap -r /` regularly and drop unnecessary capabilities.
- Alert on service crashes and on `/root` reads from processes holding capabilities.

## References

- [0xdf — EarlyAccess](https://0xdf.gitlab.io/2022/02/12/htb-earlyaccess.html)
- [IppSec — EarlyAccess](https://www.youtube.com/watch?v=P4KLqTORmIw)
- [Hack The Box — EarlyAccess](https://app.hackthebox.com/machines/earlyaccess)
