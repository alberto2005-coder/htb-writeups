---
topic: RCE en aplicaciones Electron
tags: [linux, electron, asar, ipc, prototype-pollution, rce]
---

# RCE en aplicaciones Electron

**English** | [🇪🇸 Español](electron-ipc-rce.md)

## Concept

An Electron application ships client code in `app.asar`. If the renderer can invoke dangerous IPC handlers or pollute prototypes, user-controlled input can execute commands in the main process.

## When it applies

- Electron apps downloading or processing external content.
- `contextIsolation` disabled or `nodeIntegration` enabled.
- IPC handlers passing data to `exec`, `spawn` or `shell.openExternal`.

## Procedure

1. Extract `app.asar` and review `main.js`, `preload.js` and IPC handlers.
2. Identify the exposed channel and data format.
3. Test a prototype-pollution or command payload.
4. Confirm execution in the main process.

```bash
npx asar extract app.asar app
rg -n 'ipcMain|contextBridge|exec|spawn|openExternal' app
# Send the payload to the discovered IPC channel
curl -s -X POST http://<HOST>:3000/api/run -H 'Content-Type: application/json' \
  -d '{"__proto__":{"shell":true},"cmd":"id"}'
```

## Variants

- `shell.openExternal` with a `file://` URL or dangerous scheme.
- Prototype pollution in `child_process` options.
- LFI in the resource loader.
- Unsigned updater downloading a malicious package.

## Limitations

- The IPC channel must be exposed to controllable content.
- `contextIsolation` and sandbox may block the attack.
- The Electron version must allow the gadget.

## Mitigation and detection

- Update Electron and enable `contextIsolation`/sandbox.
- Validate and allowlist IPC channels and external URLs.
- Freeze prototypes and never pass renderer data to `exec`.

## References

- <https://www.electronjs.org/docs/latest/tutorial/security>
- <https://github.com/electron/asar>
- <https://owasp.org/www-community/vulnerabilities/Prototype_Pollution>
