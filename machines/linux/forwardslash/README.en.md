---
machine: ForwardSlash
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, lfi, xxe, crypto, luks, ssh]
---

# ForwardSlash — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `backup` vhost has a file-inclusion page and an XML form vulnerable to XXE. LFI reads the source and `chiv`'s credentials; a misconfigured backup binary reads `pain`'s files. Escalation breaks a homemade cipher, opens a LUKS volume and recovers root's SSH key.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 18.04 and `80/tcp` Apache serving `forwardslash.htb`.
- The `backup.forwardslash.htb` vhost hosts an API console and an XML form.
- `/dev/` is restricted by IP and username.

## Enumeration

- `profilepicture.php` accepts a URL and renders its content; it also accepts local paths.
- `php://filter/convert.base64-encode/resource=...` reads source code.
- The backup vhost's `config.php` contains `chiv` credentials; the `/dev/` form is vulnerable to XXE.

## Foothold

Read the source of `profilepicture.php` and `/dev/`, where an FTP/SSH password for `chiv` appears. Use those credentials for SSH.

```bash
curl -s 'http://backup.forwardslash.htb/profilepicture.php'   --data-urlencode 'url=php://filter/convert.base64-encode/resource=/var/www/backup.forwardslash.htb/dev/index.php'
```

The user flag comes after pivoting to `pain`.

## Lateral movement

`chiv` can run a backup program that loads a library or configuration file insecurely. Abuse it to read `/home/pain/config.php` and recover the password; then use `su` or SSH as `pain`.

## Privilege escalation

`pain` has `encryptorinator/ciphertext` and a Python script using a byte-sum cipher. Brute-force with `rockyou.txt` until the decrypted text is readable and recover the LUKS passphrase. `sudo` allows `cryptsetup luksOpen` and `mount`; inside is a root private key.

```bash
python3 brute.py
sudo /sbin/cryptsetup luksOpen /var/backups/recovery/encrypted_backup.img backup
sudo /bin/mount /dev/mapper/backup ./mnt/
cat ./mnt/id_rsa
```

## Evidence

- Source code read with `php://filter`.
- SSH access as `chiv` and `pain`.
- Decrypted plaintext with the passphrase and root's `id_rsa` mounted.

## Lessons learned

- File inclusion must be restricted to allowed paths and extensions.
- Homemade crypto is often reversible with known plaintext or brute force.
- `sudo` on `cryptsetup` and `mount` allows reading any prepared volume.

## Mitigation and detection

- Replace dynamic includes with templates and validate paths.
- Disable external entities and DTDs in the XML parser.
- Do not grant `cryptsetup`/`mount` without controlling images and mount points.

## References

- [0xdf — ForwardSlash](https://0xdf.gitlab.io/2020/07/04/htb-forwardslash.html)
- [IppSec — ForwardSlash](https://www.youtube.com/watch?v=alJa51XylDE)
- [Hack The Box — ForwardSlash](https://app.hackthebox.com/machines/forwardslash)
