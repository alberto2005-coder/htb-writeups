---
topic: Default credentials
tags: [general, credentials, default-password, hydra, iot, enumeration]
---

# Default credentials

**English** | [🇪🇸 Español](default-credentials.md)

## Concept

Many services and devices ship with known accounts and passwords that are never changed. An admin panel, database or IoT device may accept factory credentials and grant full access.

## When it applies

- Device web panels (routers, cameras, NAS, printers).
- Services such as SSH, FTP, SMB, RDP or databases.
- Applications with demo accounts.
- Containers and templates without initial configuration.

## Procedure

1. Identify the product and version.
2. Look up the vendor's default credentials.
3. Try a small set of combinations, respecting lockout.
4. Verify access and privileges.
5. Document the account without publishing the password.

```bash
curl -s -I http://<IP>/
hydra -L users.txt -P passwords.txt -t 4 ssh://<IP>
```

## Variants

- `admin:admin`, `root:root` or `pi:raspberry`.
- Password printed on the device label.
- API with a demo token.
- Database with no password or an empty `sa`.

## Limitations

- The service must allow remote authentication.
- Modern systems force a change at first login.
- Attempt lockout can interrupt testing.
- Some panels restrict access by IP.

## Mitigation and detection

- Change credentials before exposing the service.
- Enforce unique passwords and MFA where possible.
- Inventory devices and apply a baseline configuration.
- Alert on successful logins from new IPs and factory accounts.

## References

- <https://attack.mitre.org/techniques/T1078/001/>
- <https://attack.mitre.org/techniques/T1110/001/>
- <https://www.cisa.gov/known-exploited-vulnerabilities-catalog>
- <https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password>
