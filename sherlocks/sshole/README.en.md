---
sherlock: SSHole
domain: DFIR / Unix
difficulty: Very Easy
platform: Hack The Box
evidence: Evidence from a compromised Linux jumpbox
tools: [grep, journalctl, auth.log, tcpdump]
---

# SSHole — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

A misconfigured *jumpbox* starts talking to a suspicious domain. You get evidence pulled from the server itself: work out **how they got in** and **what they did next**.

## Evidence

- Files from the jumpbox (authentication logs, history, configuration) packed in a ZIP with the usual Sherlock password.

## Method

1. **How they got in?** The box's SSH service is old and vulnerable: check the version and any anomalous connection patterns.

```bash
grep -i 'sshd' auth.log | less
grep -c 'Failed password' auth.log
```

A successful login with no preceding authentication phase (neither *password* nor *publickey*) points at an SSH server **bypass**, not brute force.

2. **The attacker's session**: correlate the source IP with the rest of the artifacts.

```bash
last -ai | head
grep '<IP>' auth.log
```

3. **What they did**: history, fresh files in `/tmp` and downloads.

```bash
cat ~/.bash_history
ls -la /tmp /var/tmp /dev/shm
```

4. **Internal recon**: the jumpbox is used to scan the network behind it; logs and traffic show sweeps against internal ranges.

5. **Persistence**: check `~/.ssh/authorized_keys`, `cron` and any added systemd units.

## What it teaches

- The jumpbox runs **Alpine Linux** and its `sshd` accepts an authentication bypass (CVE-2026-123158): Alpine's `crypt()` returns `*` when the password exceeds 256 bytes, and an account with no password also stores `*` in `/etc/shadow`. `sshd` compares `*` to `*` and **accepts the login** without knowing the password.
- The account is the service account `adminsvc`; `auth.log` never records the password sent, so the bypass is **inferred** from a successful session with no `password`/`publickey` stage.
- Afterwards the box scans `192.168.18.0/24`, runs a script and uploads to an external domain (`devv.coding.eu`): the jumpbox was the pivot, not the target.
- A jumpbox is a pivot platform: the forensic value is in the *outbound* traffic that follows.
- Comparing `auth.log` with `last` and shell history rebuilds the session.

## Pitfalls

- **Scan noise**: filter by IP and time window before drawing conclusions.
- **Rotated logs**: if the range is missing, check `.1` and `journalctl`.
- **Time zones**: `auth.log` is usually UTC; other artifacts may not be.
