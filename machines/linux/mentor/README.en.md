---
machine: Mentor
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, snmp, api, docker, jwt, privesc]
---

# Mentor — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

SNMP with the `internal` community leaks API credentials. The API authenticates as `james` and runs commands inside a container. The container runs uvicorn with `--reload`, so a model is edited to expose hashes; crack `svc`'s hash and log in over SSH. `snmpd.conf` contains the bootstrap user's password, reused for `james`, and `james` can run `/bin/sh` as root.

## Recon

```bash
nmap -Pn -sCV -p22,80,161 <IP>
```

- `22/tcp` OpenSSH on Ubuntu 22.04, `80/tcp` an HTTP API and `161/udp` SNMP.
- `snmpwalk -v2c -c public` reveals the `mentor` hostname and service contact.
- The API lives at `mentorquotes.htb` and documents authentication and quote endpoints.

## Enumeration

- `snmpbrute.py` finds the `internal` community, with more access than `public`.
- `snmpwalk` with `internal` leaks API credentials for `james`.
- Login returns a JWT; endpoints allow creating quotes and running an internal action.

## Foothold

Obtain a JWT as `james` and abuse the creation endpoint to inject a command. The reverse shell lands as root inside a Docker container.

```bash
curl -s -X POST http://mentorquotes.htb/api/v1/auth/authenticate -H 'Content-Type: application/json' -d '{"username":"james","password":"<PASSWORD>"}'
nc -lnvp 443
```

## Lateral movement

The container runs uvicorn with `--reload` and mounts `/app`. Add `password` to the `userDB` model, query the API and obtain the hashes. Crack `svc`'s hash and use it for SSH on the host.

## Privilege escalation

`/etc/snmp/snmpd.conf` contains the SNMPv3 bootstrap user's password. That password is reused for `james`, who can run `/bin/sh` with sudo.

```bash
cat /etc/snmp/snmpd.conf | grep -v '^#' | grep .
su james -
sudo -l
sudo /bin/sh
```

## Evidence

- SNMP `internal` community and API credentials.
- Root shell in the container and hashes exposed by the model.
- SSH as `svc` and `sudo /bin/sh` as `james`.

## Lessons learned

- SNMP can leak more than metrics: credentials and configuration.
- `--reload` in production enables persistent code changes.
- Bootstrap passwords are reused across services.

## Mitigation and detection

- Restrict SNMP and use strong communities or SNMPv3.
- Do not use `--reload` or mount writable code in production.
- Rotate bootstrap passwords and restrict `sudo` to specific commands.

## References

- [0xdf — Mentor](https://0xdf.gitlab.io/2023/03/11/htb-mentor.html)
- [IppSec — Mentor](https://www.youtube.com/watch?v=MjddXhMF9vg)
- [Hack The Box — Mentor](https://app.hackthebox.com/machines/mentor)
