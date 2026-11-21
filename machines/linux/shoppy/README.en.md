---
machine: Shoppy
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, nosql, mongodb, mattermost, reversing, docker, privesc]
---

# Shoppy — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The shop uses MongoDB and the login is vulnerable to NoSQL injection: `admin'||'a'=='a` authenticates as administrator without knowing the password. The panel exports users, and the same trick returns `josh`'s hash, which is cracked. That account opens Mattermost, where `jaeger`'s SSH credentials are posted. `jaeger` can run a password manager as `deploy`; the binary compares input against a 16-bit string that `strings -el` reveals, and after extracting `deploy`'s password the account is reachable. `deploy` is in the `docker` group, so a container with the host disk mounted gives root access.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,9093 <IP>
```

- `22`: OpenSSH 8.4p1 Debian.
- `80`: nginx 1.23.1, shop and Mattermost by virtual host.
- `9093`: auxiliary HTTP service.

```bash
echo '<IP> shoppy.htb mattermost.shoppy.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://shoppy.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

`/login` redirects to a form and `/admin` to `/login`. A single quote makes the response hang and return `504`, which rules out classic SQLi and points to a NoSQL query. Mattermost is published at `mattermost.shoppy.htb` with its own login form.

## Foothold

The login accepts a boolean expression in the username:

```text
username=admin'||'a'=='a&password=<PASSWORD>
```

The resulting query evaluates true for `admin` and returns a session. The panel has a user search that exports JSON; a similar injection returns `josh`'s record and MD5 hash. After cracking it, the credentials open Mattermost.

```text
username=admin'||'1'=='1&password=<PASSWORD>
```

Mattermost holds a channel with deployment credentials. The `jaeger` account logs in over SSH and reads `user.txt`.

## Lateral movement

`jaeger` can run a binary as `deploy`:

```bash
sudo -l
sudo -u deploy /home/deploy/password-manager
```

The program asks for a master password and compares it with a stored string. The binary is copied and inspected:

```bash
scp jaeger@shoppy.htb:/home/deploy/password-manager .
strings -el password-manager
```

`strings -el` shows the UTF-16 string `Sample`. Entering it prints `deploy`'s credentials, and `su deploy` switches accounts.

## Privilege escalation

`deploy` is in the `docker` group and no containers are running. The group allows mounting the host filesystem:

```bash
docker run --rm -it -v /:/mnt alpine chroot /mnt sh
```

Inside the container the user is root over the host and can read `/root/root.txt` or add an SSH key to `/root/.ssh/authorized_keys`. Another path is copying a bash binary and setting the SUID bit from the container.

## Evidence

- Login with the NoSQL expression and access to the panel.
- User export containing `josh`'s hash and the cracked password.
- `jaeger` credentials in Mattermost and an SSH session.
- `Sample` string extracted with `strings -el` and `deploy` credentials.
- `deploy` in the `docker` group and host file access from the container.

## Lessons learned

- NoSQL queries also accept operators and boolean expressions.
- An admin panel should not export hashes without additional controls.
- Password reuse chains internal services together.
- `strings` must be tried with both 8-bit and 16-bit widths.
- Membership in the `docker` group is equivalent to root on the host.

## Mitigations and detection

- Validate types and reject operators in authentication fields.
- Use salted, slow password hashing and limit exports.
- Do not reuse credentials between applications and the system.
- Restrict the `docker` group and prefer a socket proxy with least privilege.
- Monitor container creation with `-v /:/` and host mounts.
- Alert on logins containing quotes, `$ne`/`$gt` operators or unexpected JSON.

## References

- [0xdf — Shoppy](https://0xdf.gitlab.io/2023/01/14/htb-shoppy.html)
- [Hack The Box — Shoppy](https://app.hackthebox.com/machines/shoppy)
- [Knowledge — NoSQL injection](../../../knowledge/web/nosql-injection.md)
- [Knowledge — Privileged container escape](../../../knowledge/linux/docker-privileged-escape.md)
