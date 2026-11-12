---
topic: Azure AD Connect credential extraction
tags: [windows, active-directory, azure-ad-connect, adsync, credential-dump]
---

# Azure AD Connect credential extraction

**English** | [🇪🇸 Español](azure-ad-connect-dump.md)

## Concept

Azure AD Connect synchronises identities between on-prem AD and Microsoft Entra ID. Its local `ADSync` database stores credentials for the `MSOL_*` service account and the connector, reversibly encrypted. With administrative access to the server and the service keys, they can be decrypted and reused for DCSync or Entra ID access.

## When it applies

- The DC or a member server runs Azure AD Connect.
- The attacker has local/admin access or can read `ADSync.mdf`.
- The `MSOL_*` account has replication or admin rights.

## Requirements

1. Access to the Azure AD Connect server.
2. Ability to read the `ADSync` database and encryption keys.
3. A decryption tool (`AdDecrypt`, `azuread_decrypt_msol.ps1`, Mimikatz).
4. Credentials with sufficient privileges.

## Procedure

Locate the installation and database:

```powershell
Get-ChildItem 'C:\Program Files\Microsoft Azure AD Sync\Data'
```

Identify the `MSOL_*` account and service:

```powershell
Get-Service ADSync
```

Use a decryption tool to extract credentials:

```powershell
.\AdDecrypt.exe -Server <DC> -User <MSOL_USER> -Password '<MSOL_PASS>'
```

Mimikatz (`lsadump::dcsync`) also works if `MSOL_*` has replication rights.

## Variants

- **AdDecrypt**: decrypts local configuration.
- **azuread_decrypt_msol.ps1**: PowerShell script.
- **Mimikatz DCSync**: uses `MSOL_*` to replicate.
- **ADSync.mdf**: copy and analyse offline.

## Limitations

- Requires server or database access.
- Keys may rotate or be DPAPI-protected.
- `MSOL_*` may lack DCSync.
- Microsoft recommends managed service accounts.

## Mitigation

- Restrict admin access to the AAD Connect server.
- Use gMSA or managed accounts for the service.
- Audit `MSOL_*` and its permissions.
- Rotate credentials and protect `ADSync`.

## Detection

- Access to `ADSync.mdf` and the `Data` folder.
- Execution of `AdDecrypt` or decryption scripts.
- DCSync from the `MSOL_*` account.
- `MSOL_*` logons outside the sync server.

MITRE ATT&CK: T1003.006 (DCSync), T1555 (Credentials from Password Stores).

## References

- <https://learn.microsoft.com/en-us/azure/active-directory/hybrid/>
- <https://attack.mitre.org/techniques/T1003/006/>
- <https://github.com/dirkjanm/adconnectdump>
