---
topic: API — invite logic and command injection
tags: [web, api, invite, command-injection, authorization]
---

# API — invite logic and command injection

[🇪🇸 Español](api-invite-command-injection.md) | **English**

## Concept

An API recreating an invite flow often exposes generation and verification endpoints plus admin routes. If registration lets the client set `is_admin`, or the VPN endpoint passes the username to `system`, business logic becomes escalation and RCE.

## When it applies

- An invite or registration flow exists over the API.
- The client can send role or configuration fields.
- An admin endpoint generates commands or files.

## Procedure

1. Enumerate `/api` and its versions; review the obfuscated JavaScript.
2. Generate and verify an invite code.
3. Register and try `PUT /admin/settings/update` with `is_admin`.
4. Inject into the parameter that reaches the command.

```bash
curl -s -X POST 'http://<IP>/api/v1/invite/generate'
curl -s -X PUT 'http://<IP>/api/v1/admin/settings/update' -H "Cookie: PHPSESSID=<SESSION>" --data '{"is_admin":true}'
```

## Variants

- `is_admin`, `role` or `permissions` accepted at registration.
- Injection with `;`, `|`, `$()` or backticks.
- VPN download as a write vector.

## Limitations

- The role may be validated server-side.
- The command may use `escapeshellarg`.
- The account may require email verification.

## Mitigation

- Do not accept roles from the client; assign them server-side.
- Parameterize commands and avoid `system` on input.
- Audit admin endpoints and registration.

## Detection

- Registrations with `is_admin` or elevated roles.
- Requests to `/admin` from new accounts.
- Shell metacharacters in API parameters.

## References

- [OWASP — API Security Top 10](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
- [0xdf — TwoMillion](https://0xdf.gitlab.io/2023/06/07/htb-twomillion.html)
- [PortSwigger — command injection](https://portswigger.net/web-security/os-command-injection)
