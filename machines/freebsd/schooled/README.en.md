---
machine: Schooled
os: FreeBSD
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [freebsd, moodle, xss, deserialization, package-manager]
---

# Schooled — Hack The Box (FreeBSD)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Moodle chains XSS, teacher impersonation and a role vulnerability into a malicious plugin with a webshell. The database leaks bcrypt hashes, one is cracked and gives SSH as `jamie`. Root-run `pkg` plus a writable `/etc/hosts` allow serving a malicious FreeBSD package whose `+POST_INSTALL` runs as root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp    ssh     OpenSSH 7.9 (FreeBSD)
80/tcp    http    Apache httpd 2.4.46 (FreeBSD) PHP/7.4.15
33060/tcp mysqlx  MySQL X Protocol
```

## Enumeration

- The `moodle.schooled.htb` vhost serves an old Moodle with open registration.
- The version and plugins are confirmed from `config.php` and the HTTP response.
- A newly registered user can enrol as a teacher in a course.
- The teacher profile reflects unsanitised input and runs JavaScript in the administrator browser.

## Foothold

The XSS is used to create or modify an account with the manager role. Moodle role management (CVE-2020-14321) is then abused to grant administrator privileges to the controlled account.

With administrative access, a malicious plugin is installed. The ZIP contains a webshell in the version block and is uploaded through the interface; visiting the plugin path executes code as `www`.

```bash
curl -s -b cookie.txt 'http://moodle.schooled.htb/moodle/blocks/leaflet/version.php?c=id'
```

## Lateral movement

`config.php` holds the database credentials. The user table stores bcrypt hashes; they are extracted and attacked with `hashcat` against a wordlist. One hash belongs to `jamie`, who reuses the password for SSH.

```bash
mysql -u moodle -p'<DB_PASSWORD>' moodle -e 'select username,password from mdl_user;'
hashcat -m 3200 hashes.txt /usr/share/wordlists/rockyou.txt
ssh jamie@schooled.htb
```

## Privilege escalation

`jamie` may run `pkg update` and `pkg install *` with root privileges, and can write `/etc/hosts`. `devops.htb` is pointed at the attacker IP, a minimal `pkg` repository is served, and a custom package is installed.

The package contains `+MANIFEST`, `plist` and `+POST_INSTALL`; the last one runs as root during installation.

```bash
sudo -l
sudo pkg update
sudo pkg install -y <PACKAGE_NAME>
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- XSS against an administrator is worth as much as a session token.
- Role assignment must be validated server-side, not only in the UI.
- An unsigned package repository turns `pkg` into code execution.
- Writable `/etc/hosts` redirects the legitimate repository.

## Mitigations and detection

- Update Moodle and restrict plugin installation to trusted administrators.
- Validate roles and capabilities on every request.
- Sign `pkg` repositories and block changes to `/etc/hosts`.
- Log plugin installs and `pkg` runs outside maintenance windows.

## References

- [0xdf — Schooled](https://0xdf.gitlab.io/2021/09/11/htb-schooled.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+schooled)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+schooled+writeup)
