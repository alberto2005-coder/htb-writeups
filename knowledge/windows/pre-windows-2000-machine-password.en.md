---
topic: Pre-Windows 2000 computer passwords
tags: [windows, ad, machine-account, legacy, credentials]
---

# Pre-Windows 2000 computer passwords

[🌐 Español](pre-windows-2000-machine-password.md) | **English**

## Concept

Computer accounts created through the Pre-Windows 2000 flow may keep a password derived from the lowercase computer name without `$`. If the Pre-Windows 2000 Compatible Access group also has read permissions on objects, that account can read secrets such as a GMSA.

## When it applies

- A `NAME$` account created with the legacy method exists.
- The computer name is known and the password was not rotated.
- The account belongs to Pre-Windows 2000 Compatible Access.

## Procedure

1. Enumerate computer accounts and their group.
2. Try the lowercase name as the password.
3. Read permitted objects, such as a GMSA.
4. Use the secret to move to another system.

```bash
nxc smb <DC> -u 'FS01$' -p 'fs01' --shares
certipy-ad account read -u 'FS01$' -p 'fs01' -dc-ip <DC> -target <DC>
```

## Variants

- Use Kerberos instead of NTLM.
- Combine with RBCD if the account can write on the DC.
- Read `msDS-AllowedToActOnBehalfOfOtherIdentity`.

## Limitations

- The password must still be the original.
- The account must be enabled.
- Group permissions must reach the target object.

## Mitigation and detection

- Rotate computer account passwords and remove the legacy flow.
- Remove unnecessary accounts from Pre-Windows 2000 Compatible Access.
- Audit GMSA and sensitive object reads.

## References

- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-default-user-accounts>
- <https://attack.mitre.org/techniques/T1078/002/>
- <https://learn.microsoft.com/en-us/defender-for-identity/security-assessment-unsecured-account-configuration>
