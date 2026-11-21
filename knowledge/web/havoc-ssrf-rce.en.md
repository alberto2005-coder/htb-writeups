---
topic: Havoc C2 — chained SSRF and RCE (CVE-2024-41570)
tags: [web, havoc, c2, ssrf, websocket, cve-2024-41570, backfire]
---

# Havoc C2 — chained SSRF and RCE (CVE-2024-41570)

**English** | [🌐 Español](havoc-ssrf-rce.md)

## Idea

Havoc 2 0.7 accepts demon (agent) commands without checking that the `RequestID` matches a task issued by the team server. `COMMAND_SOCKET` and `COMMAND_PIVOT` are exempt from that check because they carry tunnels. An attacker can register a fake agent and open a socket to the internal administration port; the socket speaks WebSocket and reaches Havoc's authenticated RCE. On Backfire, the SSRF→WebSocket→RCE chain gave a shell as `ilya`.

## When it applies

- Havoc 2 0.7 exposed, with the admin panel on localhost or behind a proxy.
- The listener accepts agent callbacks from the attacker's network.
- A path exists to send traffic to the internal port (SSRF, tunnel, pivot).
- Havoc configuration has leaked or can be reconstructed.

## Procedure

1. Identify the Havoc listener and administration panel.
2. Register a fake agent with `DEMON_INITIALIZE`.
3. Send `COMMAND_SOCKET` or `COMMAND_PIVOT` to open the tunnel.
4. Speak WebSocket to the internal administration port.
5. Use the authenticated RCE to run commands.
6. On Backfire, continue with HardHatC2 and `iptables-save`.

## Commands

```text
POST /<listener>  → agent with command 99 (DEMON_INITIALIZE)
COMMAND_SOCKET    → socket without RequestID
COMMAND_PIVOT     → tunnel without RequestID
```

```bash
# Local tunnel to the internal panel
ssh -L 40056:127.0.0.1:40056 <USER>@<HOST>
```

## Variants

- Reuse an already registered agent to open the socket.
- Chain the SSRF with a misconfigured reverse proxy.
- Use the pivot to reach other internal services.
- Combine with the configuration leak to obtain keys and listeners.
- Apply the same pattern to other Havoc versions if the code is unchanged.

## Limitations

- Fixed versions validate the `RequestID` for socket and pivot too.
- The listener protocol and key must be known.
- The internal panel may use another port or require TLS.
- The chain depends on the fake agent being able to register.
- Actions are recorded in the team server logs.

## Mitigation

- Update Havoc to a fixed release.
- Do not expose the administration panel; separate it from the listener.
- Require authentication and validate the `RequestID` on every command.
- Segment the C2 network and limit callbacks.
- Rotate keys and review exposed configuration.

## Detection

- Agents registered from unusual IPs.
- `COMMAND_SOCKET` or `COMMAND_PIVOT` without a prior task.
- Team server connections to its own internal panel.
- Unexpected WebSocket traffic on the administration port.
- Havoc configuration reachable from file servers.

## References

- [NVD — CVE-2024-41570](https://nvd.nist.gov/vuln/detail/CVE-2024-41570)
- [0xdf — Backfire](https://0xdf.gitlab.io/2025/06/07/htb-backfire.html)
- [Havoc — Documentation](https://havocframework.com/docs/welcome)
- [Backfire writeup](../../machines/linux/backfire/README.en.md)
