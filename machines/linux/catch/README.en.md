---
machine: Catch
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, android, apk, gitea, lets-chat, credentials]
---

# Catch — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An Android application leaves an API and credentials in the APK. Static analysis reveals internal Gitea and Let's Chat services; the credentials provide access and service-configuration escalation. The chain ends with root through a task or misconfigured binary.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80,3000,5000 <IP>
```

- SSH, HTTP, Gitea and a chat service.
- The website distributes an APK.
- Virtual hosts and a documented API exist.

## Enumeration

- Download the APK and decompile it with `apktool`/`jadx`.
- `strings` and the manifest expose URLs, keys and endpoints.
- Gitea exposes repositories; Let's Chat stores messages and credentials.
- The application configuration includes a privileged user.

## Foothold

Use the APK credentials to access Gitea and review repositories. A repository contains the Let's Chat configuration or an SSH key; use it to access the host.

```bash
apktool d app.apk
jadx-gui app.apk
curl -s http://<IP>:3000/api/v1/repos/search
```

## Privilege escalation

The Let's Chat configuration or a deployment script contains credentials for a user with `sudo`. Review `sudo -l` and abuse an edit rule or service to obtain root.

```bash
sudo -l
find / -perm -4000 -type f 2>/dev/null
```

## Evidence

- Decompiled APK and extracted endpoints.
- Gitea/Let's Chat access.
- SSH or service credentials.
- Exploited `sudo` rule and root.

## Lessons

- An APK is code and configuration, not just an app.
- Embedded secrets are reused across internal services.
- Gitea and chat services often contain credentials and CI data.
- `sudo` rules are discovered after initial access.

## Mitigations and detection

- Never embed secrets in mobile applications.
- Rotate credentials and use a secret store.
- Restrict Gitea/Let's Chat to the internal network and audit access.
- Review `sudo` and separate deployment accounts.
- References: OWASP MASVS, Gitea security, HTB Catch.

## References

- <https://www.hackthebox.com/machines/Catch>
- <https://owasp.org/www-project-mobile-app-security/>
- <https://attack.mitre.org/techniques/T1552/>
- <https://attack.mitre.org/techniques/T1548/003/>
