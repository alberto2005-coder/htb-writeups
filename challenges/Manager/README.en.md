---
challenge: Manager
type: Mobile
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [mobile, android, idor, http, dynamic-analysis, password-manager]
---

# Manager — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Reference writeup; no real flag.

## TL;DR

An Android password manager trusts a client-supplied identifier to decide which vault to return. Intercepting traffic and changing the `id` reaches another user's vault and the flag.

## Prompt and surface

- Mobile, Medium, retired.
- An APK for a password manager is provided.
- The app supports registration, login and entry lookup.

```bash
apktool d manager.apk -o manager
jadx -d jadx manager.apk
```

## Reconnaissance

- The app uses HTTP and an API with user and vault endpoints.
- `jadx` shows parameters such as `userId`, `vaultId` or `id`.
- There is no local ownership check; the server decides from the supplied value.

```bash
grep -RInE 'userId|vaultId|/api/|Retrofit|OkHttp' jadx/sources | head -n 40
```

## Analysis

The client sends the vault identifier in the request. If the server does not compare it with the authenticated session, an IDOR occurs. The app neither signs the request nor binds the token to the resource.

## Exploitation

1. Register two accounts and create one entry in each.
2. Configure a proxy and intercept the vault query.
3. Replace your `id` with the other account's identifier.
4. Replay the request and read the response.

```bash
# With Burp or mitmproxy, modify the parameter and replay
GET /api/vault?id=<OTHER_ID> HTTP/1.1
Host: <HOST>
Authorization: Bearer <TOKEN>
```

The response contains the other account's entry and the flag.

## Evidence

- Original and modified request.
- Response with the other account's data, redacted.
- Vault screen, with the flag redacted.

## Lessons learned

- An opaque identifier is not an authorization check.
- The app may be only an interface: security depends on the server.
- Dynamic analysis reveals parameters that code obfuscation hides.

## Mitigations and detection

- Derive resource ownership from the session token, not the client.
- Check authorization on every query.
- Use unpredictable identifiers and access logs.
- Alert on queries for another user's resources.

## References

- <https://www.hackthebox.com/challenges/Manager>
- <https://owasp.org/www-project-top-ten/2017/A5_2017-Broken_Access_Control>
- <https://mas.owasp.org/MASTG/>
- <https://attack.mitre.org/techniques/T1213/>
