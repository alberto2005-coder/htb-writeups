---
challenge: Spiky Tamagotchi
type: Web
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [web, javascript, code-injection, authentication-bypass]
---

# Spiky Tamagotchi — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

The application evaluates JavaScript with user data to "feed" the pet. Code injection bypasses authentication and executes commands on the server.

## Prompt and surface

- Web, Easy, retired.
- Virtual pet interface with actions.
- No initial credentials.

```bash
curl -i http://<HOST>/
```

## Reconnaissance

Review requests and JS. Actions send a name/expression that the backend evaluates.

```bash
curl -X POST http://<HOST>/api/feed -H 'Content-Type: application/json' -d '{"name":"test"}'
```

## Analysis

1. Confirm expression evaluation.
2. Inject an expression that changes the authentication state.
3. Access the admin panel.
4. Run a command or read the flag file.
5. Redact the output.

```javascript
1; return process.mainModule.require('child_process').execSync('id')
```

## Root cause

The server uses `eval`/`Function` with untrusted input. Authentication logic lives in the same context, so injection can modify it.

## Local reproduction

1. Run the app.
2. Test an arithmetic expression.
3. Inject code.
4. Verify the bypass.
5. Fix and compare.

## Evidence

- Request with the expression.
- Authentication bypass.
- Command and redacted flag.

## Lessons learned

- `eval` with user input is RCE.
- Authentication must not share context with evaluated code.
- Server-side JavaScript has access to `process`.
- Blacklist validation is fragile.

## Mitigation and detection

- Remove `eval`/`Function` with user data.
- Use parsers and allowlists.
- Isolate authentication logic.
- Monitor child processes of the Node server.

## References

- <https://www.hackthebox.com/challenges/spiky-tamagotchi>
- <https://owasp.org/www-community/attacks/Code_Injection>
- <https://nodejs.org/api/child_process.html>
