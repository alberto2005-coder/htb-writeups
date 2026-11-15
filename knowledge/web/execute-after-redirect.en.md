---
topic: PHP — execution after redirect
tags: [web, php, execute-after-redirect, auth-bypass]
---

# PHP — execution after redirect

**English** | [🌐 Español](execute-after-redirect.md)

## Concept

If code sends `Location` but does not call `exit`, PHP keeps executing the rest of the script. An attacker can intercept the 302 and change the response to see protected content or perform authenticated actions.

## When it applies

- The session check calls `header('Location: ...')` without `exit`.
- The protected page body is generated afterwards.
- The response can be intercepted with a proxy.

## Procedure

1. Request the protected page without a session.
2. Intercept the 302 and change it to 200.
3. Read the form or perform the action.
4. Create a user or extract data.

## Commands

```bash
# Burp: intercept the 302 response and change it to 200 OK
curl -i http://<HOST>/accounts.php
```

## Variants

- JavaScript redirect.
- Misplaced `die()`.
- POST actions protected only by the redirect.

## Limitations

- The server may not send the body.
- The proxy must rewrite the response.
- The session may be checked before the action.

## Mitigation

- Call `exit`/`die` after the redirect.
- Enforce access control before rendering.
- Use a framework with middleware.

## Detection

- 302 responses with protected page body.
- Actions without a session from the same client.
- Requests with a modified 302.

## References

- [0xdf — Previse](https://0xdf.gitlab.io/2022/01/08/htb-previse.html)
- [OWASP — Execution after redirect](https://owasp.org/www-community/attacks/Execution_After_Redirect_(EAR))
- [PHP — header](https://www.php.net/manual/en/function.header.php)
