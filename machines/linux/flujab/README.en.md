---
machine: FluJab
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, vhosts, sqli, ajenti, ssh, screen]
---

# FluJab — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Vhost enumeration and cookie manipulation expose configuration pages. SQLi retrieves data sent by email, including Ajenti credentials. Ajenti reveals weak SSH keys; add the attacker IP to the TCP wrapper allowlist and log in with the key. Escalation escapes `rbash` and exploits `screen`.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443 <IP>
ffuf -u http://flujab.htb -H "Host: FUZZ.flujab.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
# Configuration cookie
curl -s -b "role=admin" http://flujab.htb/config/
# SQLi
sqlmap --url "http://flujab.htb/search.php?q=test" --batch --dump
# Ajenti and weak key
ssh -i debian_key <USER>@<IP>
# Escape and screen
vi
screen -version
screen -x root/root
```

## Enumeration

- Several vhosts and a cookie controlling the configuration context.
- SQLi form and internal email with credentials.
- Ajenti with weak Debian-generated SSH keys (CVE-2008-0166).

## Initial access

Enumerate subdomains and try raising privileges in the cookie to reach admin pages. SQLi returns the email with Ajenti credentials; from Ajenti download a weak SSH key and add the attacker IP to `/etc/hosts.allow`.

## Privilege escalation

The account lands in `rbash`; escape with `vi`, `less` or an environment variable. The `screen` version is vulnerable and runs commands outside the restricted session, yielding root.

## Evidence

- Vhost and manipulated cookie with configuration panel.
- Ajenti credentials and accepted SSH key.
- rbash escape and screen exploit.

## Lessons learned

- Context cookies must be validated server-side.
- Old Debian SSH keys are recoverable.
- `rbash` is not a jail if an editor or vulnerable `screen` remains.

## Mitigation and detection

- Sign and validate cookies; never trust the client role.
- Regenerate SSH keys and restrict Ajenti.
- Update screen and remove broken restricted shells.

## References

- [0xdf — FluJab](https://0xdf.gitlab.io/2019/06/15/htb-flujab.html)
- [Ajenti — Documentation](https://docs.ajenti.org/)
- [Hack The Box — FluJab](https://app.hackthebox.com/machines/flujab)
