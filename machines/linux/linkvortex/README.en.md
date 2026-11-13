---
machine: LinkVortex
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, ghost-cms, cve-2023-40028, git-dumper, symlink, toctou]
---

# LinkVortex — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

An exposed `.git` directory recovers Ghost credentials. The version is vulnerable to CVE-2023-40028, arbitrary file read through symlinks. The leaked configuration gives SSH access and a `sudo` script with a TOCTOU race leads to root.

## Recon

```bash
nmap -Pn -sC -sV -p22,80 <IP>
```

- SSH and HTTP.
- Vhosts `linkvortex.htb` and `dev.linkvortex.htb`.

## Enumeration

- The web root contains an accessible `.git` directory.
- `git-dumper` recovers the repository and its history.

```bash
git-dumper http://linkvortex.htb/.git repo/
git log --all --oneline
```

- The history contains credentials for a Ghost user.

## Foothold

Ghost 5.x is vulnerable to CVE-2023-40028: an authenticated user can upload a symlink and read arbitrary files through the download path.

```bash
# Authenticate at /ghost and prepare the symlink upload
curl -s -b cookies.txt "http://linkvortex.htb/ghost/api/admin/files/upload/"
```

`config.production.json` or the equivalent configuration is read to obtain the system user's password.

## Lateral movement

The Ghost password is reused for SSH.

```bash
ssh bob@linkvortex.htb
```

## Privilege escalation

`sudo -l` shows a cleanup script that checks a file and then operates on it. The file can be replaced by a symlink between the check and the use.

```bash
sudo -l
ln -sf /etc/sudoers.d/<FILE> /checked/path
sudo /usr/local/bin/<CLEANUP_SCRIPT>
```

The TOCTOU race allows writing or modifying a privileged file and obtaining root.

## Evidence

- Exposed `.git` and recovered commits.
- Symlink upload request.
- Configuration file read, with secrets redacted.
- `sudo -l` and script execution.
- Redacted flag.

## Lessons learned

- An exposed `.git` leaks far more than source code.
- Symlinks break validations based only on paths.
- A separate check and use creates a TOCTOU window.

## Mitigations and detection

- Block `.git` and other version-control metadata.
- Update Ghost to a fixed version.
- Resolve paths and reject symlinks in privileged scripts.
- Audit `sudo` scripts that manipulate temporary files.

## References

- <https://www.hackthebox.com/machines/linkvortex>
- <https://nvd.nist.gov/vuln/detail/CVE-2023-40028>
- <https://attack.mitre.org/techniques/T1552/001/>
- <https://attack.mitre.org/techniques/T1548/001/>
