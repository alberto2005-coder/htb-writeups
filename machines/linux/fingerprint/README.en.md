---
machine: Fingerprint
os: Linux
difficulty: Insane
platform: Hack The Box
state: Retired
tags: [linux, web, hql, hibernate, xss, java-deserialization, jwt, aes-ecb, cmatch, privesc]
---

# Fingerprint — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A long multi-stage chain. An execute-after-redirect (EAR) and a directory traversal in `/admin` provide file reads; code analysis reveals HQL injection (Hibernate) and XSS. Boolean injection extracts data, a custom Java serialized payload is built and a shared JWT secret is abused to execute and get a shell as `www-data`. To move to `john`, the SUID `cmatch` counts regex matches in any file and acts as an oracle to extract his SSH key. As `john`, the backup of the secure application under `/root` is readable. That application uses AES-ECB with the secret appended to the username, allowing a byte-at-a-time ECB attack to leak the secret, sign an administrator cookie, use a file read and reach root over SSH.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,8080 <IP>
```

- `22`: OpenSSH 7.6p1 Ubuntu.
- `80`: Werkzeug 1.0.1 on Python 2.7.17, a Flask application.
- `8080`: Sun GlassFish 5.0.1, a Java application.

```bash
echo '<IP> fingerprint.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://fingerprint.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

The Flask site has login, registration and an `/admin` panel that displays logs. The log viewer parameter escapes the intended directory and reads files. On registration, the application redirects and processes data before checking the session (EAR), easing access to internal parts.

Code and traffic analysis shows:

- HQL queries built from user input.
- XSS in the profile.
- A JWT secret shared between the Flask and Java applications.
- A users table with a hidden field extractable through boolean injection.

## Foothold

HQL injection enumerates users and fields. To execute code, a Maven project builds a Java serialized object with the library available in GlassFish and signs a valid JWT for the Java application. The payload is sent to an endpoint that deserializes it, and the chain ends in a shell as `www-data`.

```bash
mvn clean package
java -cp target/<ARTIFACT>.jar <MAIN_CLASS> '<COMMAND>'
```

The shell reads both applications' code and confirms the shared secret.

## Lateral movement

`www-data` can run `/usr/bin/cmatch` as `john`. The binary takes two arguments, a file and a regular expression, and returns the number of matches. It is SUID, so it reads files `www-data` cannot open, and the match count becomes an oracle to extract content byte by byte.

It reads `/home/john/.ssh/id_rsa` and reconstructs the private key; SSH then logs in as `john`.

```bash
cmatch /home/john/.ssh/id_rsa '^-----BEGIN'
cmatch /home/john/.ssh/id_rsa '^<PREFIX>'
```

## Privilege escalation

`john` can read `/var/backups/flask-app-secure.bak`, a ZIP with the code of the application running as root on `8088`. The code builds `username,secret,true|false` and encrypts it with AES-ECB. Since ECB encrypts equal blocks identically, a byte-at-a-time attack works: choose a username of controlled length and compare cookie blocks to recover the secret character by character.

With the secret, an administrator cookie is signed, the secure application's file read retrieves root's SSH key, and SSH provides root.

```bash
python3 exploit_ecb.py --url http://127.0.0.1:8088
curl -s http://127.0.0.1:8088/admin -H 'Cookie: <COOKIE>'
```

## Evidence

- Traversal in `/admin` and reads of `/etc/passwd` and the code.
- HQL injection with boolean responses.
- JWT signed with the shared secret and a shell as `www-data`.
- SUID `cmatch` and extraction of `john`'s key.
- `flask-app-secure.bak` backup and analysis of the AES-ECB encryption.
- Recovered secret, administrator cookie and read of root's key.
- `id` with UID 0.

## Lessons learned

- Chaining minor vulnerabilities (EAR, traversal, XSS) can lead to execution.
- HQL is not SQL: syntax and objects differ, but injection remains possible.
- A SUID binary that leaks information can be a read oracle.
- AES-ECB leaks patterns and must not be used for cookies or identifiers.
- A backup of a privileged application is source code and often the key to root.

## Mitigations and detection

- Parameterize HQL and validate types; never concatenate input into queries.
- Fix the check order so the session is validated before processing data.
- Escape the profile and use `HttpOnly`, `Secure` and `SameSite` cookies.
- Remove unnecessary SUID bits and review binaries that read arbitrary files.
- Replace AES-ECB with AES-GCM using a random IV and authentication.
- Protect privileged application backups and do not share secrets across services.
- Alert on SSH key reads and access to `/console` or internal panels.

## References

- [0xdf — Fingerprint](https://0xdf.gitlab.io/2022/05/14/htb-fingerprint.html)
- [IppSec — Fingerprint](https://www.youtube.com/watch?v=YBabDbyk3eo)
- [Hack The Box — Fingerprint](https://app.hackthebox.com/machines/fingerprint)
- [Knowledge — HQL injection](../../../knowledge/web/hql-injection.en.md)
