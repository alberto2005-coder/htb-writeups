---
topic: Node-RED — execution through Function nodes
tags: [web, node-red, rce, nodejs, iot]
---

# Node-RED — execution through Function nodes

[🌐 Español](node-red-rce.md) | **English**

## Concept

The Node-RED editor lets users create flows with `function` nodes that run JavaScript on the server. If the editor is exposed without authentication, or with default credentials, a flow can be deployed that uses `child_process` to run commands.

## When it applies

- Port 1880 reachable with `/red` lacking `adminAuth`.
- Default or reused credentials.
- IoT applications exposing Node-RED on the internal network.

## Procedure

1. Open `/red` and check whether authentication is required.
2. Review `/flows` and the version at `/settings`.
3. Create a flow with an `inject` node and a `function` node.
4. Use `child_process.execSync` and return the output.
5. Deploy the flow and trigger the inject node.

## Commands

```javascript
// Function node
const { execSync } = global.get('child_process') || require('child_process');
msg.payload = execSync('id').toString();
return msg;
```
```bash
curl -s http://<HOST>:1880/flows
curl -s http://<HOST>:1880/settings
```

## Variants

- Import a malicious flow from `flows.json`.
- Use the `exec` node when installed.
- Modify `settings.js` when the filesystem is writable.

## Limitations

- The editor may enforce `adminAuth` or sit behind a proxy.
- The version may block `require` inside Function nodes.
- The flow needs an `inject` or HTTP endpoint to trigger it.

## Mitigation

- Enable `adminAuth` and change default credentials.
- Do not expose the editor to the Internet; segment the IoT network.
- Run Node-RED as an unprivileged user.

## Detection

- New flows containing `function`, `exec` or `http in` nodes.
- Connections to `/red` and `/flows` from unusual hosts.

## References

- <https://nodered.org/docs/user-guide/runtime/securing-node-red>
- <https://attack.mitre.org/techniques/T1059/>
