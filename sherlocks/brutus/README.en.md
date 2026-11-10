---
sherlock: Brutus
domain: SOC
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [dfir, linux, ssh, brute-force, auth-log, log-analysis]
---

# Brutus — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Investigation notes; platform answers are not reproduced.

## Scenario

An Internet-facing Linux server received an abnormal volume of authentication attempts. A disk image (or a set of system logs) is provided and the job is to rebuild the attack: where it came from, which accounts were tried, and whether anyone ever got in.

## Evidence

- Disk image or a copy of `/var/log`.
- `auth.log` / `secure` covering the incident.
- `wtmp` plus the `utmp.py` parser shipped with the challenge.
- The system user list (`/etc/passwd`).

```bash
sha256sum brutus.zip
ls -la logs/
wc -l logs/auth.log
```

## Investigation

### 1. Scope the incident

In `auth.log`, SSH failures have a very stable shape:

```text
Failed password for invalid user <name> from <IP> port <p> ssh2
Failed password for <user> from <IP> port <p> ssh2
```

```bash
grep "Failed password" auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -rn
```

The IP with thousands of attempts is the source; the rest is Internet noise. That also bounds the first/last attempt window.

### 2. Which accounts were targeted

```bash
grep "Failed password" auth.log | grep -oP 'for (invalid user )?\K\S+' | sort | uniq -c | sort -rn
```

Names absent from `/etc/passwd` are a generic wordlist (`admin`, `test`, `oracle`…); names that exist suggest a valid-user list or prior enumeration.

### 3. Did anyone get in?

The key question of the box:

```bash
grep -E "Accepted (password|publickey)" auth.log
grep -c "Failed password" auth.log
```

With no `Accepted` line inside the attack window, the brute force **never succeeded**: the impact is exposure and noise, not compromise. Also check `last`, `lastb` and open `sshd` sessions.

### 4. Host context

```bash
grep -E "new user|useradd|groupadd" auth.log
ls -la /home
```

This rules out an account created by the attacker during the same period.

## Findings

- Credential-stuffing/brute force against SSH from a single IP.
- Successful `Accepted password for root`, a persistence account and a downloaded enumeration script.
- Immediate fix: disable password login, move SSH to keys, `fail2ban`, and network-level restrictions.

## Lessons

- `auth.log` answers "did they get in?" precisely: a single `Accepted` line flips the whole conclusion.
- Enumerating valid users before the attack matters as much as the attack.
- A brute-force case is solved by counting and grouping, not by reading line by line.
