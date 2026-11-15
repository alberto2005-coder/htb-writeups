---
machine: Registry
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, docker-registry, bolt-cms, restic, privesc]
---

# Registry — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A private Docker registry with weak credentials allows downloading the Bolt CMS image. The image contains an SSH key and password for `bolt`; Bolt 3.6.4 allows a webshell upload and `www-data`. `www-data` can run `restic backup` as root, and a copy of `/root` exposes the flag and root SSH key.

## Recon

```bash
nmap -Pn -sCV -p22,80,443 <IP>
wfuzz -u http://registry.htb -H 'Host: FUZZ.registry.htb' -w subdomains.txt
```

- `22` SSH, `80`/`443` nginx.
- `wfuzz` finds `docker.registry.htb` and `bolt.registry.htb`.
- The TLS certificate reveals `docker.registry.htb`.

## Enumeration

The registry answers on `/v2/` and `/v2/_catalog` with weak credentials. List `bolt-image`, download the manifest and layers, and extract the filesystem.

```bash
curl -k --user <USER>:<PASS> https://docker.registry.htb/v2/_catalog
curl -k --user <USER>:<PASS> https://docker.registry.htb/v2/bolt-image/manifests/latest
```

## Foothold

The layers contain an SSH key and a password for `bolt`. Log in over SSH.

```bash
ssh -i bolt.key bolt@registry.htb
```

## Lateral movement

`/bolt` runs Bolt CMS 3.6.4. The panel accepts the recovered credentials; an upload/execution flaw lets you place a webshell and get `www-data`.

```bash
curl 'http://registry.htb/bolt/files/shell.php?cmd=id'
```

## Privilege escalation

`www-data` can run `restic backup` as root:

```bash
sudo /usr/bin/restic backup -r rest0xdf /root/root.txt
```

Create a local repository, back up `/root/root.txt` and `/root/.ssh/id_rsa`, and read them with `restic dump`. The key logs in as root.

```bash
restic -r /tmp/restic/0xdf dump latest /root/root.txt
```

## Evidence

- Docker registry and weak credentials.
- Image with SSH key and `bolt` password.
- Bolt CMS and webshell.
- `restic backup` as root.
- `/root` backup and root.

## Lessons learned

- A private Docker registry can leak image secrets.
- Images include deployment keys and credentials.
- Old Bolt CMS allows upload-based execution.
- A weak `restic` sudo rule copies arbitrary files as root.

## Mitigation and detection

- Authenticate the registry and avoid default credentials.
- Keep secrets out of images; use external secrets.
- Update Bolt CMS and validate uploads.
- Restrict `restic` to specific paths and repositories.

## References

- [0xdf — Registry](https://0xdf.gitlab.io/2020/04/04/htb-registry.html)
- [IppSec — Registry](https://www.youtube.com/watch?v=w0h0QYswFNA)
- [Hack The Box — Registry](https://app.hackthebox.com/machines/registry)
