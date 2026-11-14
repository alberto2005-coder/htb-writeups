---
topic: OpenBSD — authentication bypass and S/Key
tags: [openbsd, authentication, bypass, xlock, skey]
---

# OpenBSD — authentication bypass and S/Key

[🌐 Español](authentication-bypass.md) | **English**

## Concept

A flaw in `auth_userokay()` can make BSD auth services accept authentication without a valid password. In OpenKeyS it is combined with `xlock` and S/Key to move from user to root.

## When it applies

- OpenBSD without the 2019 patches.
- Services using BSD auth, such as `su`, `doas` or `xlock`.
- S/Key enabled for an account.

## Procedure

1. Identify the OpenBSD version.
2. Test authentication against BSD auth services.
3. Check `xlock` and the S/Key configuration.
4. Obtain a session and review privileges.
5. Escalate with the matching local flaw.

## Commands

```bash
uname -a
cat /etc/skey/skeys 2>/dev/null
xlock -help
```

## Variants

- Remote bypass in SSH or `su`.
- Local escalation through `xlock`.
- Abusing S/Key for persistence.

## Limitations

- A vulnerable version is required.
- The service must use auth_userokay.
- The 2019 patches mitigate it.

## Mitigation

- Patch OpenBSD with the 2019 errata.
- Review S/Key and `xlock` configuration.
- Limit exposed services.

## Detection

- Successful logins without a valid password.
- Anomalous `xlock` and S/Key use.

## References

- <https://www.openbsd.org/errata.html>
- <https://nvd.nist.gov/vuln/detail/cve-2019-19521>
