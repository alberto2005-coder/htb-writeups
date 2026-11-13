---
topic: chromedriver session hijack
tags: [linux, chromedriver, froxlor, session-hijack, devtools, reload-cmd]
---

# chromedriver session hijack

**English** | [🇪🇸 Español](chromedriver-session-hijack.md)

## Concept

An unauthenticated local `chromedriver` exposes the DevTools port and allows control of another user's browser. If that browser has an active session in an administrative panel such as Froxlor, the attacker can steal the cookie and use privileged functions such as `reload_cmd` to execute commands.

## When it applies

- `chromedriver` listening on localhost.
- A browser with an active administrative session.
- Froxlor or another panel with system actions.
- Ability to reach the port from the machine.

## Procedure

1. Enumerate local processes and ports.
2. Identify `chromedriver` and its session.
3. Query `/json` for the `webSocketDebuggerUrl`.
4. Steal cookies or run JavaScript in the tab.
5. Use the session to invoke `reload_cmd` or an equivalent action.

```bash
ps aux | grep -i chromedriver
curl -s http://127.0.0.1:9515/json
curl -s http://127.0.0.1:9515/json/version
```

## Variants

- DevTools on port 9222.
- Hijacking a Froxlor session with `reload_cmd`.
- Exfiltrating cookies and CSRF tokens.
- Using `Page.navigate` for administrative actions.

## Limitations

- The port must be reachable.
- The session must be authenticated and active.
- The panel must allow the privileged action.
- The cookie may be bound to an IP or expire.

## Mitigation and detection

- Do not expose `chromedriver` without authentication.
- Close sessions and browsers after automated tasks.
- Restrict `reload_cmd` and validate input.
- Audit DevTools access and unusual administrative actions.

## References

- <https://chromedevtools.github.io/devtools-protocol/>
- <https://froxlor.org/>
- <https://attack.mitre.org/techniques/T1185/>
