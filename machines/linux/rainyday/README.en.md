---
machine: RainyDay
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, idor, docker, flask, jail-escape, use-after-free, unicode, privesc]
---

# RainyDay — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An IDOR leaks hashes; crack `gary`'s and enter a container manager. From a container, reach a development API that applies regex to files and turn it into arbitrary read; leak the Flask key, forge `jack`'s session and escape the jail to read his SSH key. On the host, a Python use-after-free gives `jack_adm`, and a hash program with Unicode truncation allows guessing the salt and cracking root's password.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22` SSH and `80` nginx with `rainyday.htb`.
- `ffuf` finds `rainycloud.htb` and `dev.rainycloud.htb`.
- The main site is a cloud container company.

## Enumeration

- An API IDOR returns `jack` and `gary` hashes.
- Crack `gary` with `john`; the account reaches the container panel.
- Create an `alpine-python` container and get a shell in it.

```bash
john --wordlist=rockyou.txt hashes.txt
```

## Foothold

From the container, reach the development API, which applies a regex to a file. Build a Python script that turns the response into arbitrary read and read the Flask source for the `SECRET_KEY`.

```bash
flask-unsign --unsign --cookie '<COOKIE>' -w <(echo '<SECRET>')
```

## Lateral movement

Sign a cookie as `jack` and access his `secrets` container. The jail shares the host filesystem and a `cwd` symlink points to `/home/jack`; read the private SSH key and enter the host.

```bash
flask-unsign --sign --cookie "{'username': 'jack'}" --secret <SECRET>
ssh -i jack_key jack@rainyday.htb
```

## Privilege escalation

On the host, `safe_python` is SUID and has a use-after-free. The exploit gives a shell as `jack`, and run under `safe_python` it gives `jack_adm`. That user can run `hash_password.py` as root; the program truncates Unicode input and uses a secret salt. Generate a password list and brute-force the salt until it matches root's hash.

```bash
./exploit
sudo /usr/bin/safe_python ./exploit
python3 brute_salt.py
```

## Evidence

- IDOR and `jack`/`gary` hashes.
- Container and development API with arbitrary read.
- Flask `SECRET_KEY` and `jack` cookie.
- Jail escape and SSH key.
- Use-after-free, Unicode truncation and root.

## Lessons learned

- An API IDOR can leak every hash.
- Development APIs with regex are file read.
- A container jail does not isolate if it shares the filesystem.
- SUID programs and Unicode handling widen escalation.

## Mitigation and detection

- Authorize every object and never return hashes.
- Remove development APIs and validate paths.
- Isolate containers with namespaces and minimal mounts.
- Review SUID binaries and normalize Unicode before hashing.

## References

- [0xdf — RainyDay](https://0xdf.gitlab.io/2023/02/18/htb-rainyday.html)
- [IppSec — RainyDay](https://www.youtube.com/watch?v=E5TOeiCnGkE)
- [Hack The Box — RainyDay](https://app.hackthebox.com/machines/rainyday)
