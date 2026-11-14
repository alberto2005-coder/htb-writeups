---
machine: Extension
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, laravel, hash-length-extension, docker, gitea, password-reset]
---

# Extension — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Three vhosts (snippets, RoundCube and Gitea) leak users and hashes; a shared password grants access and an IDOR reveals the Gitea repository. Password reset only changes the last characters, so hundreds of tokens accumulate and `charlie`'s account is taken over. In the code, SHA-256(secret+email) protects a command injection; a hash length extension attack bypasses it and yields a shell in the container, where `docker.sock` allows reading root's SSH key.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p22,80 <IP>
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt -u http://<IP> -H "Host: FUZZ.<DOMAIN>"
```

## Enumeration

- `snippet.htb`, `mail.snippet.htb` and `dev.snippet.htb` run the app, RoundCube and Gitea.
- The user API returns hashes; a shared one cracks to a weak password.
- Reset tokens only vary in their last digits and do not invalidate earlier tokens.

## Initial access

After logging in with the shared password, an IDOR exposes a snippet with Gitea credentials and `jean`'s name. Hundreds of reset requests are sent for `charlie` and the tokens are tested; because several remain valid, the administrator password is changed and Gitea is accessed.

## Privilege escalation

The repository contains `AdminController::validateEmail`, which runs `ping` with the email domain when the SHA-256(secret+email) checksum matches. With a known checksum and a secret length of 40, `hash_extender` appends `@$(...)` while preserving the signature. The resulting shell is `application` inside a container with `docker.sock`; a privileged container with `/` mounted reads root's private key from the host.

## Evidence

- Hashes and users returned by the API.
- `charlie` reset using an accumulated token.
- Hash-extension bypass and container with `/host`.

## Lessons learned

- Reset tokens must be random, single-use and invalidate previous ones.
- A secret-prefixed checksum is not a secure MAC.
- An accessible `docker.sock` is equivalent to host root.

## Mitigation and detection

- Invalidate old tokens and compare in constant time.
- Use HMAC instead of concatenating secrets with user input.
- Never mount the Docker socket into application containers.

## References

- [0xdf — Extension](https://0xdf.gitlab.io/2023/03/18/htb-extension.html)
- [IppSec — Extension](https://www.youtube.com/watch?v=qNsbf3EmLrA)
- [Hack The Box — Extension](https://app.hackthebox.com/machines/extension)
