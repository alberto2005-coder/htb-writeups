---
machine: Secret
os: Linux
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [linux, web, jwt, command-injection, suid, crash-dump, file-descriptors, privesc]
---

# Secret — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The site's Git repository exposes its code; analysis reveals the JWT signing secret. An administrator token reaches internal functions, one with command injection, and yields a shell as `dasith`. `/opt` contains a SUID `count` with its source and a `valgrind.log`; it is abused in two ways: reading files through the process's open file descriptors or crashing it and reading the content from the core dump.

## Reconnaissance

```bash
nmap -Pn -sCV -p22,80,3000 <IP>
```

- `22`: OpenSSH 8.2p1 Ubuntu.
- `80`: nginx 1.18.0, main site.
- `3000`: Node.js Express, API.

```bash
echo '<IP> secret.htb' | sudo tee -a /etc/hosts
feroxbuster -u http://secret.htb -w /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
```

## Enumeration

The main site is a landing page with documentation. The `.git` repository is exposed and downloaded with `git-dumper` or manually. The code shows:

- JWT generation and verification.
- The signing secret.
- Administrative routes and an `exec` call with user input.
- The API on port `3000`.

## Foothold

The secret signs a JWT with the administrator role and opens internal routes. One route takes a parameter passed to a system command; a separator runs a reverse shell as `dasith`.

```bash
python3 -c "import jwt; print(jwt.encode({'role':'admin'}, '<SECRET>', algorithm='HS256'))"
```

## Lateral movement

There is no second host. `dasith` has no `sudo`. `/opt` contains three files:

- `count`: a root SUID binary that counts characters, words and lines.
- `code.c`: the binary's source.
- `valgrind.log`: output from a Valgrind run.

## Privilege escalation

`count` opens the given file and saves a summary but never closes the descriptor. `/proc/<PID>/fd/<N>` then reaches a readable file inside a directory that cannot be traversed, such as `/root/.profile`; a root-only file like `root.txt` remains protected by its permissions.

The second path is a crash: the binary enables core dumps with `prctl(PR_SET_DUMPABLE, 1)`, and the dump contains the file it read as root. If the core lands in an accessible path with loose permissions, the privileged content is read from the dump.

```bash
/opt/count
# enter /root/root.txt and trigger the fault
ls -l /var/crash/
cat /var/crash/_opt_count.*.crash
```

## Evidence

- Exposed `.git` and JWT secret in the code.
- Administrator token accepted by the API.
- Command injection and `id` as `dasith`.
- `find / -perm -4000` showing `/opt/count`.
- Source code and `valgrind.log`.
- Descriptor or core-dump read and `id` with UID 0.

## Lessons learned

- An exposed `.git` repository leaks code and secrets.
- Signing JWTs with a static secret allows forging any role.
- A SUID binary that opens privileged files can leak them through descriptors.
- Core dumps from privileged processes can contain sensitive data.
- SUID plus `prctl` and dumps is an escalation path.

## Mitigations and detection

- Do not publish `.git` or secrets in the repository; use environment variables.
- Rotate the JWT secret and validate `iss`, `aud` and expiry.
- Avoid `exec` with user input; use APIs and allowlists.
- Remove unnecessary SUID bits and review those that open files.
- Disable core dumps for privileged processes or restrict their path.
- Alert on `.git` downloads, administrator tokens and crashes under `/opt`.

## References

- [0xdf — Secret](https://0xdf.gitlab.io/2022/03/26/htb-secret.html)
- [IppSec — Secret](https://www.youtube.com/watch?v=byYZl9CSFtM)
- [Hack The Box — Secret](https://app.hackthebox.com/machines/secret)
- [Knowledge — SUID: file descriptors and crash dumps](../../../knowledge/linux/suid-fd-crashdump.en.md)
