---
machine: Cybermonday
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, nginx, laravel, jwt, redis, docker, privesc]
---

# Cybermonday — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An nginx off-by-slash leaks `.env` and the repository; mass assignment gives admin and access to a webhooks API using JWTs. Algorithm confusion signs as admin, and a webhook with CRLF talks to Redis to poison the Laravel session and run code. From the container, enumerate a Docker registry, pull the API image and leak `john`'s password; a poorly validated `docker compose` script mounts the host.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` nginx with `cybermonday.htb`.
- The site is a Laravel shop; `feroxbuster` finds `/api` and admin routes.
- An nginx off-by-slash allows reading `.env` and `.git`.

## Enumeration

- The profile updates every field and accepts `isAdmin=true` (mass assignment).
- As admin, `webhooks-api-beta.cybermonday.htb` appears.
- The API uses RS256 JWTs and publishes its public key in JWKS.

## Foothold

Verification trusts the token's algorithm. Switch to HS256 and sign with the public key as the secret (algorithm confusion), obtaining an admin token. With it, create a `sendRequest` webhook that performs SSRF.

A CRLF in the webhook URL talks to Redis and modifies the Laravel session. Use `phpggc` to build an object and get execution as `www-data` inside the container.

## Lateral movement

The internal network has a Docker registry. Weak credentials list `bolt-image`/the API image, download it and review the code. An extra endpoint with a special header allows file reads and leaks `john`'s password, which works over SSH.

## Privilege escalation

`john` can run `/opt/secure_compose.py` as root with any `.yml`. The script validates the compose file, but the check can be bypassed to launch a container with the host filesystem mounted or `apparmor:unconfined`. Inside the container, read `/root/root.txt` or write a key.

```bash
sudo /opt/secure_compose.py /tmp/docker-compose.yml
```

## Evidence

- Off-by-slash and `.env`.
- Mass assignment and webhooks API.
- JWT algorithm confusion.
- SSRF/CRLF against Redis and Laravel RCE.
- Docker registry and `john`'s password.
- `secure_compose.py` and root.

## Lessons learned

- An nginx off-by-slash exposes files outside the root.
- Mass assignment can grant administrative roles.
- Trusting the JWT algorithm breaks asymmetric validation.
- CRLF in a URL can turn SSRF into Redis access.
- Validating a compose file is not enough if host mounts are allowed.

## Mitigation and detection

- Fix the nginx alias and block `.env`/`.git`.
- Allowlist fields and roles.
- Pin the JWT algorithm and validate `kid`/issuer.
- Isolate Redis and validate webhook URLs.
- Run compose unprivileged with restricted volumes.

## References

- [0xdf — Cybermonday](https://0xdf.gitlab.io/2023/12/02/htb-cybermonday.html)
- [IppSec — Cybermonday](https://www.youtube.com/watch?v=VNMn5bXA8XY)
- [Hack The Box — Cybermonday](https://app.hackthebox.com/machines/cybermonday)
