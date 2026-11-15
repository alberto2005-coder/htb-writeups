---
topic: Ansible — command injection in ansible-galaxy
tags: [linux, ansible, ansible-galaxy, command-injection, privesc]
---

# Ansible — command injection in ansible-galaxy

**English** | [🌐 Español](ansible-galaxy-command-injection.md)

## Concept

A wrapper that builds an `ansible-galaxy role install` command with a controlled name can allow command injection if it does not use `execve` with separate arguments. The role name becomes part of a shell string.

## When it applies

- A root binary or script receives a role name/JSON.
- The command is built as a string and run with `system`/`shell`.
- The name or path is controllable.

## Procedure

1. Review the wrapper and expected JSON.
2. Try `; id` in the name.
3. Turn it into an interactive shell.
4. Read the flag or write a key.

## Commands

```bash
echo '{"role": "x; bash"}' > /tmp/r.json
sudo /opt/runner2/runner2 /tmp/r.json
```

## Variants

- Injection in the role path.
- `ansible-galaxy` with a controlled `--role-file`.
- Symlinks in the install directory.

## Limitations

- The wrapper may validate the name.
- It may use `subprocess` with a list.
- The role may need to exist or fail after injection.

## Mitigation

- Use `subprocess` with a list and no shell.
- Validate role names with a regex.
- Do not run wrappers as root.

## Detection

- `;`, `$()` or `|` in role names.
- `ansible-galaxy` processes with child shells.
- Writes to `/root` from the wrapper.

## References

- [0xdf — Intuition](https://0xdf.gitlab.io/2024/09/14/htb-intuition.html)
- [Ansible — galaxy CLI](https://docs.ansible.com/ansible/latest/cli/ansible-galaxy.html)
- [CWE-78 — OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
