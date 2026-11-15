---
topic: Minecraft — RCON and plugin secrets
tags: [windows, minecraft, rcon, log4shell, java]
---

# Minecraft — RCON and plugin secrets

**English** | [🌐 Español](minecraft-rcon.md)

## Concept

RCON is a Minecraft administrative protocol that runs commands on the server. If its password is in a plugin or `server.properties` and is reused, an attacker with server or JAR access can execute commands as the Minecraft user or pivot to another context.

## When it applies

- Port `25575` is open or reachable from another container.
- A plugin/JAR with configuration or credentials can be downloaded.
- Log4Shell or another RCE already provided server access.

## Procedure

1. Enumerate Minecraft and the admin panel.
2. Download and decompile the plugin to find `rcon.password`.
3. Connect to RCON and run a test command.
4. Use `RunasCs` or the service context to escalate.

## Commands

```bash
nmap -Pn -sCV -p25565,25575 <IP>
mcstatus <IP>:25565
unzip plugin.jar -d plugin && jadx plugin | grep -ri "rcon\|password"
mcrcon -H <IP> -P 25575 -p "<PASS>" "whoami"
mcrcon -H <IP> -P 25575 -p "<PASS>" "powershell -c whoami"
```

## Variants

- Use RCON to run a PowerShell script or download a binary.
- Reuse the password against the Crafty web panel.
- Combine it with Log4Shell for the first shell.

## Limitations

- RCON may be bound to loopback.
- The password may differ from the panel password.
- The server may run as an unprivileged user.

## Mitigation

- Disable RCON or bind it to loopback.
- Rotate passwords and keep them out of plugins.
- Run Minecraft under a low-privilege service account.

## Detection

- Connections to `25575` from hosts other than the panel.
- RCON commands spawning processes or downloading files.
- Plugins with plaintext credentials.

## References

- [Minecraft — RCON](https://minecraft.wiki/w/Server.properties#enable-rcon)
- [0xdf — Crafty](https://0xdf.gitlab.io/2024/06/15/htb-crafty.html)
- [CWE-798 — Hard-coded Credentials](https://cwe.mitre.org/data/definitions/798.html)
