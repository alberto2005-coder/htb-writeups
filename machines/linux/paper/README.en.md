---
machine: Paper
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, wordpress, rocket-chat, cve-2019-17671, polkit]
---

# Paper — Hack The Box (Linux)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

A private WordPress draft leaks through `?static=1` and contains Rocket.Chat credentials. The vulnerable Rocket.Chat version allows reading messages/files and gaining access; the final escalation abuses polkit (CVE-2021-3560).

## Enumeration

```bash
nmap -p- --min-rate 5000 -T4 <IP>
nmap -sC -sV -p22,80,443 <IP>
```

Add `paper.htb` and `office.paper.htb` to hosts. WordPress runs on the office vhost; enumerate with `wpscan` and `feroxbuster`.

## Initial access

WordPress exposes an unpublished draft through the `static` parameter:

```bash
curl 'http://office.paper.htb/?static=1'
```

The content includes Rocket.Chat credentials. Log in at `chat.paper.htb` and enumerate channels and users. The Rocket.Chat version is vulnerable to CVE-2019-17671 (unauthorised message/file read). An SSH password is found in a message, granting access as `dwight`.

## Lateral movement

```bash
ssh dwight@paper.htb
```

Review processes, jobs and local credentials. Identify the polkit version and prepare the escalation.

## Privilege escalation

Polkit 0.105-25 is vulnerable to CVE-2021-3560. Create an admin user by racing the identity check:

```bash
time ./poc.sh
```

The script creates a UID 0 user or adds privileges; then use `su` to become root. It can also be exploited manually with `dbus-send` and a race.

## Evidence

- Leaked WordPress draft.
- Rocket.Chat session and message with redacted credential.
- SSH access as `dwight`.
- `pkexec --version` and PoC output (redacted).

## Lessons learned

- WordPress drafts may be reachable through preview parameters.
- Rocket.Chat must be updated and message reads restricted.
- Chat credentials get reused over SSH.
- Old polkit enables reliable local escalation.

## Mitigation and detection

- Restrict previews and drafts to authenticated users.
- Update Rocket.Chat and WordPress.
- Never share credentials over chat.
- Update polkit and monitor unexpected user creation.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2019-17671>
- <https://nvd.nist.gov/vuln/detail/CVE-2021-3560>
- <https://www.hackthebox.com/machines/paper>
