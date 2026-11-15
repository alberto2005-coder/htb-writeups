---
machine: Vessel
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, nodejs, mysql, owa, crio, privesc]
---

# Vessel — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`/.git` under `/dev` allows rebuilding the source with `git-dumper`. The mysqljs login is vulnerable to type confusion (`password.password=1`) and grants panel access, where OWA 1.7.3 has CVE-2022-24637. A PyInstaller binary and a protected PDF leak SSH credentials; SUID `pinns` enables escape with CVE-2022-0811.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 22.04 and `80/tcp` nginx serving `vessel.htb`.
- The site is a Node.js application with a login and a `/dev` section.
- `/.git/HEAD` is reachable and the repository contains the source code.

## Enumeration

- `git-dumper http://vessel.htb/.git ./src` reconstructs the application.
- The login uses `mysqljs` and compares `password` with the database value; a nested object changes the query.
- The source includes OWA credentials and the path to a PDF backup.

## Foothold

Send `username=admin&password[password]=1` to bypass the comparison and enter the panel. There, exploit OWA 1.7.3 with CVE-2022-24637 to write PHP and obtain a shell as `www-data`.

```bash
curl -d 'username=admin&password[password]=1' http://vessel.htb/login
python3 CVE-2022-24637.py http://vessel.htb/owa/
# webshell under /owa/data/... and reverse shell
```

## Lateral movement

The shell allows reading a PyInstaller binary and a protected PDF. Extract the code with `pyinstxtractor` and crack the PDF with `pdfcrack`; the resulting credentials work for SSH as `steve`.

## Privilege escalation

`pinns` is SUID and vulnerable to CVE-2022-0811: it allows manipulating `core_pattern` and running a program when a process crashes. Prepare a core handler that copies `/bin/bash` with SUID and trigger a crash.

```bash
find / -perm -4000 -type f 2>/dev/null
# pinns -d ... with the CVE-2022-0811 payload
cat /proc/sys/kernel/core_pattern
```

## Evidence

- Source rebuilt from `/.git`.
- Login with `password[password]=1` and webshell in OWA.
- `steve` credentials and exploited SUID `pinns`.

## Lessons learned

- An exposed `.git` reveals application source and credentials.
- Type coercion in a driver can turn an object into a true condition.
- A misconfigured CRI-O SUID binary enables container escape or privilege escalation.

## Mitigation and detection

- Block `/.git` and never deploy the repository into the webroot.
- Validate types and use parameterized queries at login.
- Update CRI-O/pinns and review unnecessary SUID binaries.

## References

- [0xdf — Vessel](https://0xdf.gitlab.io/2023/03/25/htb-vessel.html)
- [IppSec — Vessel](https://www.youtube.com/watch?v=ZANv0DlrTN8)
- [Hack The Box — Vessel](https://app.hackthebox.com/machines/vessel)
