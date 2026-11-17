---
machine: Seventeen
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, sqli, docker, roundcube, npm, privesc]
---

# Seventeen — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `exam.seventeen.htb` vhost has a boolean SQL injection in `?p=take_exam&id=`. Dumping `erms_db` and `db_sfms` yields Kelly's student number and password, which log into School File Management System. The app allows a PHP upload; the welcome PDF mentions a webmail at `mastermailer.seventeen.htb`. Roundcube 1.4.2 is vulnerable to CVE-2020-12640: the installer includes a user-controlled path as a plugin and executes the file. Upload `papers.php` to a known directory and point the installer at `papers`, giving a `www-data` shell in a container. Configuration files leak MySQL credentials and `mark`'s password, reused over SSH. The npm module `db-logger` contains `kavi`'s password; `kavi` can run `/opt/app/startup.sh` as root, and the script installs `loglevel` from the registry in `/home/kavi/.npmrc`. Publishing a malicious `loglevel` to a local Verdaccio writes an SSH key to `/root/.ssh/authorized_keys`.

## Recon

```bash
nmap -Pn -sCV -p22,80,8000 <IP>
```

- `22` OpenSSH 7.6p1 Ubuntu 18.04.
- `80` Apache 2.4.29 serving an education company site.
- `8000` Apache 2.4.38 in a container; returns `403`.

```bash
echo '<IP> seventeen.htb exam.seventeen.htb oldmanagement.seventeen.htb mastermailer.seventeen.htb' \
  | sudo tee -a /etc/hosts
```

`wfuzz` finds the `exam` vhost. `feroxbuster` finds `/admin`, `/uploads`, `/database` and `/classes`.

## Enumeration

The exam site uses `/?p=take_exam&id=1`. A quote changes the response; `id=1' AND 4755=4755 AND 'a'='a` returns the normal page while `4755=4756` returns “Unknown Exam ID”. It is boolean SQL injection. `sqlmap --technique B` enumerates four databases: `erms_db`, `db_sfms`, `roundcubedb` and `information_schema`.

```bash
sqlmap -u 'http://exam.seventeen.htb/?p=take_exam&id=1' -p id --technique B --batch --dbs
```

`db_sfms.student` contains student number `31234` and an MD5 hash that cracks. Those credentials log into School File Management System.

## Foothold

The app allows file uploads and offers a welcome PDF, which mentions `https://mastermailer.seventeen.htb/`. The webmail is Roundcube 1.4.2. Its installer accepts `_plugins_qwerty` as a plugin path; CVE-2020-12640 includes a controlled PHP file.

Upload `papers.php` into `files/31234/papers/` and point the installer at the `papers` directory:

```text
_plugins_qwerty=../../../../../../../../../var/www/html/oldmanagement/files/31234/papers
```

Loading any Roundcube page executes the webshell and returns a reverse shell as `www-data` inside a Docker container.

## Lateral movement

`/var/www/html` contains `employeemanagementsystem`, `mastermailer` and `oldmanagement`. Connection files hold MySQL credentials; the `ems` password is also `mark`'s host password:

```bash
ssh mark@seventeen.htb
```

`/var/mail` has a message for `kavi` mentioning a private npm registry and an “old logger”. `npm search log --registry http://127.0.0.1:4873` shows `db-logger` by `kavigihan`. Installing `db-logger` exposes `logger.js`, which contains a MySQL password that is also `kavi`'s password.

## Privilege escalation

`kavi` can run `/opt/app/startup.sh` as root. The script checks `db-logger` and `loglevel`, installs anything missing and starts Node. `~/.npmrc` points at the local registry, but can be changed to a local Verdaccio instance.

Create a `loglevel` package with a version above the installed one and an `index.js` that writes an SSH key to `/root/.ssh/authorized_keys` and exports `log`, `debug` and `warn`. Publish it to the local Verdaccio, change `.npmrc` and run:

```bash
sudo /opt/app/startup.sh
```

The script installs the malicious package as root and executes its `require`. Then log in over SSH as root.

## Evidence

- Different boolean responses in `take_exam`.
- Dump of `db_sfms.student` and SFMS login.
- PDF with the webmail URL.
- `papers.php` uploaded and a `www-data` shell in the container.
- MySQL, `mark` and `db-logger` credentials.
- `startup.sh` installing `loglevel` and a key in `/root/.ssh/authorized_keys`.

## Lessons learned

- A slow boolean SQL injection is still enough to dump several databases.
- Welcome documents and internal mail reveal services and usernames.
- An exposed Roundcube installer can turn an LFI into RCE.
- npm modules with hardcoded credentials leak reused passwords.
- A startup script that installs dependencies as root executes code from a controllable registry.

## Mitigations and detection

- Parameterise `id` and do not return condition-dependent messages.
- Remove `/installer` from Roundcube and update to a fixed release.
- Never store credentials in code; use environment variables and a secret manager.
- Block PHP execution in upload directories.
- Run `npm install` without privileges, pin versions and use an allowlisted registry.
- Detect `sqlmap`, installer access, PHP uploads, modified `.npmrc` and new packages in `/opt/app/node_modules`.

## References

- [0xdf — Seventeen](https://0xdf.gitlab.io/2022/09/24/htb-seventeen.html)
- [IppSec — Seventeen](https://www.youtube.com/watch?v=U-2nI6wSPOE)
- [NVD — CVE-2020-12640](https://nvd.nist.gov/vuln/detail/CVE-2020-12640)
- [Hack The Box — Seventeen](https://app.hackthebox.com/machines/seventeen)
