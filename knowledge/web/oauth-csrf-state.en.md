---
topic: OAuth — CSRF through missing state
tags: [web, oauth, csrf, state, account-linking]
---

# OAuth — CSRF through missing state

**English** | [🌐 Español](oauth-csrf-state.md)

## Concept

The `state` parameter binds the authorization response to the session that started the flow. If it is not validated, an attacker can make the victim complete a flow with the attacker's code and link their account, or vice versa, take over the victim's account.

## When it applies

- The OAuth server does not validate `state` or accepts it empty.
- The application supports account linking or provider login.
- The callback can be predicted or reused.

## Procedure

1. Start the flow and capture the callback.
2. Check whether `state` is validated or changes.
3. Make the victim visit the attacker's authorization URL.
4. Use the linked account to access the application.

## Commands

```bash
# Start the flow and observe state
curl -i "http://<HOST>/oauth/authorize?client_id=<ID>&redirect_uri=http://<HOST>/callback"
# Callback without state
curl -i "http://<HOST>/oauth/callback?code=<CODE>"
# Send the URL to the bot or victim
```

## Variants

- Login CSRF: the victim logs in with the attacker's account.
- Account linking: link the attacker's account to the victim.
- Reuse a fixed or predictable `state`.

## Limitations

- A random, session-bound `state` blocks the attack.
- PKCE and SameSite reduce the surface.
- The flow may require user interaction.

## Mitigation

- Generate a random `state` and validate it against the session.
- Use PKCE and `SameSite=Lax` cookies.
- Require explicit confirmation when linking accounts.

## Detection

- Callbacks without `state` or with repeated values.
- Authorization links opened from email or chat.
- Account linking from unusual locations.

## References

- [OAuth 2.0 — Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)
- [PortSwigger — OAuth CSRF](https://portswigger.net/web-security/oauth)
- [0xdf — Oouch](https://0xdf.gitlab.io/2020/08/01/htb-oouch.html)
