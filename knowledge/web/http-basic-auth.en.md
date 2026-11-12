---
topic: HTTP Basic Auth brute force
tags: [web, basic-auth, brute-force, hydra]
---

# HTTP Basic Auth brute force

**English** | [🇪🇸 Español](http-basic-auth.md)

## Concept

HTTP Basic Auth sends `user:password` in Base64. Without TLS anyone can read it; without rate limiting, a wordlist can be tried until it hits.

## When it applies

- A `401` response with `WWW-Authenticate: Basic realm="..."`.
- No lockout after attempts.
- Weak or default passwords.

## Requirements

1. Protected URL.
2. Likely username.
3. Wordlist and Hydra/ffuf.

## Procedure

```bash
curl -i http://<HOST>/
hydra -l admin -P /usr/share/wordlists/rockyou.txt <HOST> http-get /
```

With `ffuf`:

```bash
ffuf -u http://<HOST>/ -w users.txt:USER -w passwords.txt:PASS -e -mode clusterbomb
```

On `200`, authenticate:

```bash
curl -u '<user>:<password>' http://<HOST>/
```

## Variants

- **Basic Auth in APIs**: send `Authorization: Basic`.
- **Unknown user**: enumerate via messages or timing.
- **Weak rate limit**: add delays and rotate IPs.
- **Default credentials**: try before the wordlist.

## Limitations

- TLS prevents sniffing, not brute force.
- A WAF may block after few attempts.
- The account may lock out.
- The wordlist may miss the password.

## Mitigation

- TLS and modern auth (OIDC/MFA).
- Rate limiting and progressive lockout.
- Strong, unique passwords.
- Monitor 401s and alert.

## Detection

- Many `401`s from one IP.
- Hydra/ffuf user-agents.
- Attempts with common usernames.
- Successful access after a failure burst.

MITRE ATT&CK: T1110 (Brute Force), T1078 (Valid Accounts).

## References

- <https://www.rfc-editor.org/rfc/rfc7617>
- <https://github.com/vanhauser-thc/thc-hydra>
- <https://attack.mitre.org/techniques/T1110/>
