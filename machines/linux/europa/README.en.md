---
machine: Europa
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, sqli, preg_replace, cron, php]
---

# Europa — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The login is vulnerable to SQLi and allows admin access. A legacy `preg_replace` call with `/e` executes PHP code and yields a shell; a root cron runs a missing script that `www-data` can write.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443 <IP>
gobuster dir -u https://europa.htb -w /usr/share/wordlists/dirb/common.txt -k
# Login bypass
curl -k -d "username=admin' OR 1=1-- -&password=x" https://europa.htb/login.php
# Execution through preg_replace /e
curl -k "https://europa.htb/admin/search.php?q=system('id')"
pspy64 -pf -i 1000
```

## Enumeration

- HTTPS portal with a login and admin panel.
- Parameters reaching an old PHP function with `preg_replace` and `/e`.
- A root cron references a missing script in a writable path.

## Initial access

`' OR 1=1-- -` bypasses authentication. In the panel, the vulnerable parameter goes through `preg_replace` with `/e`, which evaluates the replacement; send a reverse shell and obtain `www-data`.

## Privilege escalation

`pspy` shows a root cron running a missing script in a controllable path. Create the file with a shell and the next run executes it as root.

## Evidence

- Login bypass with SQLi.
- `id` execution through `preg_replace /e`.
- Script created in the cron path and root shell.

## Lessons learned

- Deprecated PHP modifiers turn a replacement into execution.
- A cron calling a missing file is a door when the directory is writable.
- Authentication SQLi remains a viable entry point.

## Mitigation and detection

- Migrate to `preg_replace_callback` and update PHP.
- Use absolute paths and non-writable directories in cron.
- Parameterize queries and require MFA on the panel.

## References

- [0xdf — Europa](https://0xdf.gitlab.io/2021/02/02/htb-europa.html)
- [PHP — preg_replace](https://www.php.net/manual/en/function.preg-replace.php)
- [Hack The Box — Europa](https://app.hackthebox.com/machines/europa)
