---
topic: DPAPI
tags: [windows, dpapi, credentials, master-key, mimikatz, forensics]
---

# DPAPI

**English** | [🇪🇸 Español](dpapi.md)

## Concept

Data Protection API encrypts secrets with keys derived from the user profile or the machine. DPAPI blobs are decrypted with a master key, which in turn depends on the user's password or the domain recovery key. It is common in browser, Zoom and enterprise application credentials.

## When it applies

- Credentials saved by applications.
- A compromised user profile.
- Access to master keys and blobs.
- Recovery with a domain key or `NTDS.dit`.

## Procedure

1. Locate blobs and master keys in the profile.
2. Identify the user or machine scope.
3. Obtain the user's password or hash.
4. Decrypt the master key.
5. Use the key to decrypt the blobs.

```powershell
Get-ChildItem "$env:APPDATA\Microsoft\Protect" -Recurse -Force
mimikatz.exe "dpapi::masterkey /in:<MASTERKEY> /sid:<SID> /password:<PASSWORD>" "dpapi::cred /in:<BLOB>"
```

## Variants

- User DPAPI with a password.
- Machine DPAPI with system credentials.
- Domain recovery key or `NTDS.dit`.
- Browser, Zoom, RDP or scheduled-task blobs.

## Limitations

- Without the password or master key, decryption fails.
- Password rotation changes the keys.
- The profile must be complete.
- Some blobs require the application context.

## Mitigation and detection

- Protect profiles and master keys.
- Use short-lived credentials and MFA.
- Audit access to `Protect` and to blobs.
- Alert on bulk DPAPI reads and Mimikatz use.

## References

- <https://learn.microsoft.com/en-us/windows/win32/seccrypto/cryptprotectdata>
- <https://github.com/gentilkiwi/mimikatz/wiki/howto-~-decrypt-credentials-file>
- <https://attack.mitre.org/techniques/T1555/003/>
