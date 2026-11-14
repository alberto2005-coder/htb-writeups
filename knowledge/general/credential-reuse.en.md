---
topic: Credential reuse
tags: [general, credentials, reuse, default-credentials, spraying, authentication]
---

# Credential reuse

**English** | [🇪🇸 Español](credential-reuse.md)

## Concept

Password reuse and default credentials move an attacker from one service to another without exploiting a vulnerability. A finding in an application, database or configuration file can open SSH, SMB, WinRM or an administrative panel.

## When it applies

- Credentials obtained from an application or backup.
- Users sharing the same password across systems.
- Services with `admin/admin` or `guest` accounts.
- Exposed administrative panels.

## Procedure

1. Inventory users and discovered credentials.
2. Test reuse against reachable services.
3. Check lockout policies before testing multiple accounts.
4. Prioritise service and administrator accounts.
5. Document each access and avoid lockouts.

```bash
nxc smb <HOST> -u <USER> -p '<PASSWORD>' --continue-on-success
nxc winrm <HOST> -u <USER> -p '<PASSWORD>'
ssh <USER>@<HOST>
```

## Variants

- Default passwords on routers, ERP or panels.
- Reuse between a database and the operating system.
- Password spraying with one password across accounts.
- Credentials in environment variables or repositories.

## Limitations

- Account lockouts can interrupt testing.
- MFA may block access even with a valid password.
- Reuse may be limited by segmentation.
- A successful login does not always mean privileges.

## Mitigation and detection

- Ban default credentials and enforce rotation.
- Use unique passwords and a secrets manager.
- Apply MFA and progressive lockout.
- Alert on distributed attempts and logins from new hosts.

## References

- <https://attack.mitre.org/techniques/T1078/>
- <https://attack.mitre.org/techniques/T1110/003/>
- <https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password>
