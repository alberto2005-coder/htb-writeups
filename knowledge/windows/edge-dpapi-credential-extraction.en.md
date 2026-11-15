---
topic: Edge credentials and DPAPI
tags: [windows, dpapi, edge, credentials, privesc]
---

# Edge credentials and DPAPI

[🌐 Español](edge-dpapi-credential-extraction.md) | **English**

## Concept

Edge encrypts saved passwords with DPAPI. In a user context they can be decrypted with the user's master key; with an administrative account or a profile dump, recovered credentials are often reused in the domain.

## When it applies

- Execution as the profile owner is available.
- Edge's `User Data` directory is accessible.
- A DPAPI master key exists or can be obtained from the DC.

## Procedure

1. Locate `Local State` and the `Login Data` folder.
2. Extract the encrypted key and decrypt it with the master key.
3. Open the SQLite database and decrypt the passwords.
4. Test the credentials against SMB, WinRM or LDAP.

```bash
DonPAPI.py DOMAIN/user:'<PASSWORD>'@<IP>
# o con el perfil montado:
python3 dpapi.py masterkey -file <MASTERKEY> -sid <SID> -password '<PASSWORD>'
python3 dpapi.py credential -file <CREDENTIAL> -key <KEY>
```

## Variants

- Use `SharpDPAPI` or `Mimikatz` on the host.
- Decrypt Credential Manager blobs.
- Combine with an open Edge session.

## Limitations

- Without the master key the blob cannot be decrypted.
- The account must be able to load the profile.
- Credentials may be absent.

## Mitigation and detection

- Disable browser password saving.
- Protect DPAPI keys and limit profile access.
- Use managed credentials and MFA.

## References

- <https://learn.microsoft.com/en-us/windows/win32/secdoc/dpapi>
- <https://github.com/login-securite/DonPAPI>
- <https://attack.mitre.org/techniques/T1555/003/>
