---
topic: VS Code — malicious extensions in sync jobs
tags: [windows, vscode, extension, sync, privesc]
---

# VS Code — malicious extensions in sync jobs

**English** | [🌐 Español](vscode-extension-privesc.md)

## Concept

VS Code installs extensions from a `.vsix` and runs their code on activation. If a sync job reads packages from a writable share, an attacker publishes an extension with the same identifier and executes in the context of the syncing user, often with more privileges.

## When it applies

- An extension or profile share is writable.
- A process runs `code --install-extension` or syncs profiles.
- The extension activates when the editor or workspace opens.

## Procedure

1. Locate the share and sync process.
2. Create an extension with `package.json` and an `activate` function.
3. Package the `.vsix` and place it on the share.
4. Wait for installation and command execution.

## Commands

```bash
smbclient //<HOST>/<SHARE> -U <USER>%<PASS>
vsce package
smbclient //<HOST>/<SHARE> -U <USER>%<PASS> -c "put extension.vsix"
code --install-extension extension.vsix
# package.json
{"name":"ext","publisher":"x","version":"1.0.0","engines":{"vscode":"*"},"main":"./extension.js","activationEvents":["*"]}
```

## Variants

- Replace a legitimate extension with a higher version.
- Use an already trusted profile or workspace.
- Abuse VS Code tasks that run commands on open.

## Limitations

- The share must allow writes.
- The extension must match the VS Code version.
- The user must restart or open the workspace.

## Mitigation

- Sign and validate extensions; use an internal marketplace.
- Mount sync shares read-only.
- Review extensions and workspace trust.

## Detection

- New `.vsix` files on sync shares.
- Extensions with `activationEvents: ["*"]`.
- VS Code child processes running commands.

## References

- [VS Code — Extension manifest](https://code.visualstudio.com/api/references/extension-manifest)
- [0xdf — Checkpoint](https://0xdf.gitlab.io/2026/10/24/htb-checkpoint.html)
- [CWE-829 — Inclusion of Functionality from Untrusted Control Sphere](https://cwe.mitre.org/data/definitions/829.html)
