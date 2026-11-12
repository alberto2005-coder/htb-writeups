---
machine: Forgotten
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web
state: Retired
pwned: false
tags: [linux, limesurvey, docker, plugin-upload, sudo]
---

# Forgotten — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real credentials or flags.

## Summary

An uninstalled LimeSurvey instance. The installation wizard allows pointing it at a local MySQL instance and creating a superadmin account. From the admin panel, a malicious plugin provides RCE in the container. An environment variable with the LimeSurvey password is reused for the host user, and a `sudo` rule leads to root.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -p 22,80 -sCV <IP>
```

Port 80 serves the LimeSurvey installer. The application runs in a Debian container, while SSH points to an Ubuntu host.

```bash
curl -s http://<IP>/ | head
```

## Initial access

Start a MySQL instance reachable from the target and complete the wizard:

```bash
docker run --rm -p 3306:3306 -e MYSQL_ROOT_PASSWORD=<PASSWORD> mysql:5.7
```

Configure the database, create the administrator and finish the installation. Then upload a plugin containing PHP code:

```text
plugins/ExampleSettings/ExampleSettings.php
```

Activate it from the admin panel and trigger a reverse shell:

```bash
nc -lnvp 443
```

The shell lands as `limesvc` inside the container.

## Escalation

Review environment variables and processes:

```bash
env
cat /proc/1/environ | tr '\0' '\n'
sudo -l
```

The `LIMESURVEY_PASS` password is reused for the host's `limesvc` user. Log in over SSH:

```bash
ssh limesvc@<IP>
```

On the host, `sudo -l` shows a rule allowing a command as root; abuse it for a shell.

## Flags

- `user.txt`: `<USER_FLAG>`
- `root.txt`: `<ROOT_FLAG>`

## Lessons

- An unfinished installer allows creating the administrator.
- Plugin upload is code execution without validation.
- Container environment variables often hold reused secrets.
- A compromised container can reach the host through reuse.

## Detection and mitigation

- Block the installer after deployment and require authentication.
- Validate and sign plugins; restrict writes to `upload/plugins`.
- Never reuse container and host passwords; use dedicated secrets.
- Review `sudo` rules and run containers unprivileged.

## References

- <https://0xdf.gitlab.io/2025/09/16/htb-forgotten.html>
- <https://docs.limesurvey.org/Plugins+at+a+glance>
- <https://attack.mitre.org/techniques/T1505/003/>
