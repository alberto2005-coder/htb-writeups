---
topic: Zabbix — API, scripts and agent execution
tags: [linux, zabbix, api, command-execution, suid, privesc]
---

# Zabbix — API, scripts and agent execution

[🇪🇸 Español](zabbix-api-command-injection.md) | **English**

## Concept

The Zabbix API authenticates users and allows creating scripts that run on the server or an agent. An account with weak credentials can create a script with a reverse shell and run it on the agent host; agent permissions determine the resulting user.

## When it applies

- The Zabbix UI or API is reachable.
- A password has been guessed or reused.
- The agent accepts remote scripts (`EnableRemoteCommands=1`).

## Procedure

1. Authenticate with `user.login` and get the token.
2. List hosts and scripts with `host.get` and `script.get`.
3. Create a script and run it with `execute_on: 0`.
4. Enumerate SUID and writable scripts for root.

```bash
curl -s -X POST 'http://<IP>/zabbix/api_jsonrpc.php' -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"user.login","params":{"user":"<USER>","password":"<PASSWORD>"},"id":1}'
```

## Variants

- `script.create` with a command and `execute_on: 0`.
- `history.get` to read internal data.
- A SUID calling `system` without an absolute path.
- A writable backup script run by cron.

## Limitations

- The account needs API and script permissions.
- The agent may have remote commands disabled.
- The patched version restricts scripts.

## Mitigation

- Strong credentials and MFA on Zabbix.
- Disable remote commands and limit scripts.
- Absolute paths and least privilege on SUID and scripts.

## Detection

- `script.create` and executions from the API.
- Child processes of the agent.
- New SUID files or modified backup scripts.

## References

- [Zabbix — API](https://www.zabbix.com/documentation/current/en/manual/api)
- [0xdf — Zipper](https://0xdf.gitlab.io/2019/02/23/htb-zipper.html)
- [MITRE ATT&CK — T1059](https://attack.mitre.org/techniques/T1059/)
