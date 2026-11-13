---
topic: Linux forensic artifacts
tags: [forensics, linux, auth-log, bash-history, cron, git, incident-response]
---

# Linux forensic artifacts

**English** | [🇪🇸 Español](linux-artifacts.md)

## Concept

On Linux, access and activity remain in `auth.log`, `syslog`, web-service logs, `.bash_history`, cron and Git history. Correlating time, user, IP and command reconstructs an intrusion without relying on a single file.

## When it applies

- A Linux server with suspicious activity.
- A Git repository with unexplained changes.
- SSH access and privilege escalation.
- Persistence through cron or services.

## Procedure

1. Fix the time zone and hash the evidence.
2. Review SSH logins, `sudo` and user creation.
3. Read `.bash_history` and web-service logs.
4. Inspect cron, systemd and processes.
5. Review Git: `log`, `reflog`, `diff` and branches.

```bash
grep -Ei 'accepted|failed|new user|sudo' auth.log
cat /home/<USER>/.bash_history
crontab -l; ls -la /etc/cron.*
git log --all --oneline --decorate
git reflog --date=iso
```

## Variants

- A deleted history or one linked to `/dev/null`.
- Commands run without an interactive shell.
- Changes committed with `git commit --amend`.
- Persistence in `systemd`, cron or `.profile`.

## Limitations

- History may be disabled or tampered with.
- Logs rotate and may be missing.
- A root attacker can alter timestamps.
- Git does not record uncommitted changes.

## Mitigation and detection

- Centralise logs and protect their integrity.
- Audit `sudo`, SSH and user creation.
- Monitor cron, systemd and repository changes.
- Alert on empty histories, new IPs and after-hours commits.

## References

- <https://attack.mitre.org/techniques/T1070/003/>
- <https://git-scm.com/docs/git-reflog>
- <https://www.sans.org/white-papers/linux-forensics/>
