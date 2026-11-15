---
machine: Checker
os: Linux
difficulty: Hard
platform: Hack The Box
state: Retired
tags: [linux, web, teampass, bookstack, race-condition, privesc]
---

# Checker — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

Teampass 3.0.0.22 is vulnerable to CVE-2023-1545: SQLi in search dumps hashes, one cracks and opens BookStack and SSH. SSH requires 2FA, but BookStack CVE-2023-6199 enables SSRF and a PHP filter oracle to read `.google_authenticator` from a backup. For root, `check_leak` uses shared memory and a race condition lets us inject the command it runs as root.

## Recon

```bash
nmap -Pn -sCV -p22,80,8080 <IP>
```

- `22` SSH, `80` BookStack and `8080` Teampass.
- `ffuf` with `Host: FUZZ.checker.htb` confirms `checker.htb` and `books.checker.htb`.
- Teampass shows its version and login.

## Enumeration

- Teampass search is vulnerable to CVE-2023-1545.
- The SQLi dumps `login`, `pw` and `token` from `teampass_users`.
- Hashes are bcrypt; one cracks with a dictionary.

## Foothold

With the cracked password, log in to Teampass and read an entry with `reader` credentials for SSH and BookStack. SSH asks for a TOTP code, but BookStack can read `/backup/home_backup/home/reader/.google_authenticator`.

```bash
bash cve-2023-1545.sh http://<IP>:8080
hashcat -m 3200 hashes.txt rockyou.txt
```

## Lateral movement

BookStack 23.10.2 is vulnerable to CVE-2023-6199. Use SSRF with `php://filter` and an error oracle to reconstruct the 2FA file; then generate the code and log in over SSH.

```bash
ssh reader@checker.htb
```

## Privilege escalation

`check_leak` is a root binary that creates a predictable shared-memory key, reads a string and passes it to a query. A looping process writes a command into that memory during the race window; the next run executes it as root.

```bash
while true; do ./poison; done
sudo /usr/local/bin/check_leak
```

## Evidence

- Teampass version and CVE-2023-1545 SQLi.
- Cracked hash and `reader` credentials.
- `php://filter` over the backup and TOTP code.
- Poisoned shared memory and root shell.

## Lessons learned

- A compromised password manager hands over credentials for several systems.
- SSRF with an error oracle can read files without direct output.
- A predictable `shm` key and a `sleep` turn a root binary into an exploitable race.

## Mitigation and detection

- Update Teampass and BookStack; parameterize queries.
- Do not store home backups where the application can read them.
- Use `shmget` with IPC_PRIVATE and never execute commands from shared memory.

## References

- [0xdf — Checker](https://0xdf.gitlab.io/2025/05/31/htb-checker.html)
- [IppSec — Checker](https://www.youtube.com/watch?v=mywIX1F1Cr8)
- [Hack The Box — Checker](https://app.hackthebox.com/machines/checker)
