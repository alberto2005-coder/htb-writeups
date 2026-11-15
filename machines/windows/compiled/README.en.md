---
machine: Compiled
os: Windows
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [windows, web, git, gitea, hashcat, privesc]
---

# Compiled — Hack The Box (Windows)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference note; no real flags or credentials.

## TL;DR

A site that compiles Git repositories uses a vulnerable Git version; a repository with malicious submodules executes code on the server. Gitea's local SQLite database leaks user hashes, one reused over SSH. Escalation abuses a vulnerable Visual Studio installation for SYSTEM.

## Recon

```bash
nmap -Pn -sCV -p22,80,3000,5985 <IP>
```

- Ports: `22/tcp` SSH, `80/tcp` HTTP, `3000/tcp` Gitea and `5985/tcp` WinRM.
- Services: Build portal, local Gitea and Windows OpenSSH.
- Technologies: Git, Gitea, SQLite, PBKDF2-SHA256, Visual Studio.

## Enumeration

- `compiled.htb` allows account registration and a repository URL submission.
- Gitea listens on `127.0.0.1:3000`.
- `gitea.db` holds users and password hashes.
- OpenSSH is exposed for system users.

## Foothold

Create a repository with a submodule and a hook that exploits CVE-2024-32002. When the build is requested, Git clones the submodule and runs the hook as the service user.

```bash
# Local repository with a malicious submodule and hook
python3 create_cve_2024_32002_repo.py
# Submit the repository URL to the build site
curl -s -b cookies.txt -F "repo=http://<IP>/repo.git" http://compiled.htb/compile
```

## Lateral movement

The shell exposes the Gitea database and its hashes. Reformat the PBKDF2 hash, crack it and reuse the password over SSH.

## Privilege escalation

Enumeration shows a vulnerable Visual Studio installation. Abuse its updater/installer component to execute code as SYSTEM.

```bash
whoami /priv
wmic product get name,version
# Locate the installer and run the exploit for the installed version
C:\\Program Files (x86)\\Microsoft Visual Studio\\Installer\\vs_installer.exe
```

## Evidence

- Accepted repository and hook callback.
- Gitea user table and cracked hash.
- SSH access and SYSTEM shell.

## Lessons learned

- A service that clones repositories is a critical trust boundary.
- Internal SQLite databases often hold reused password hashes.
- Installed development software widens the escalation surface.

## Mitigation and detection

- Patch Git and disable hooks/submodules for untrusted clones.
- Isolate Gitea and use slow, uniquely salted hashes.
- Patch Visual Studio and run services with low-privilege accounts.

## References

- [0xdf — Compiled](https://0xdf.gitlab.io/2024/12/14/htb-compiled.html)
- [IppSec — Compiled](https://www.youtube.com/watch?v=aG_N2ZiCfxk)
- [Hack The Box — Compiled](https://app.hackthebox.com/machines/compiled)
