---
topic: AD Recycle Bin and deleted objects
tags: [active-directory, windows, recycle-bin, deleted-objects, credentials, dfir]
---

# AD Recycle Bin: deleted objects as a credential source

**English** | [🇪🇸 Español](ad-recycle-bin.md)

## Idea

Deleting an object in Active Directory does not erase it: it becomes a **tombstone** and stays in the directory with its attributes for a while. With the optional **Recycle Bin** feature enabled the object keeps *all* attributes and can be restored; without it, only a few survive (the rest are stripped on deletion). Either way, an attacker allowed to read deleted objects can recover passwords, descriptions and group memberships the organisation believes gone.

## When it applies

- The domain has the `Recycle Bin Feature` optional feature enabled and there are accounts with the **AD Recycle Bin** role (or `Domain Admin`).
- Someone wants quiet persistence: restore a deleted account instead of creating a new one.
- Forensics: rebuild which accounts existed, when they were deleted and what rights they held.
- Typical case: a temporary admin account is deleted instead of disabled, and its password still works.

## Commands

Check whether the feature is enabled:

```powershell
Get-ADOptionalFeature -Filter 'Name -eq "Recycle Bin Feature"' |
  Select-Object Name, EnabledScopes
```

List deleted objects with every attribute:

```powershell
Get-ADObject -filter 'isDeleted -eq $true' -includeDeletedObjects -property * |
  Select-Object Name, sAMAccountName, whenCreated, whenChanged, lastKnownParent
```

Look for a specific attribute (say, a legacy one holding a password):

```powershell
Get-ADObject -filter 'isDeleted -eq $true -includeDeletedObjects -property *' |
  Where-Object { $_.cascadeLegacyPwd } |
  Select-Object Name, cascadeLegacyPwd
```

Restore the object and read it as a live account:

```powershell
Restore-ADObject -Identity '<GUID>'
Get-ADUser -Identity '<sAMAccountName>' -Properties *
```

LDAP equivalent, using the `LDAP_SERVER_SHOW_DELETED_OID` control (`1.2.840.113556.1.4.417`):

```bash
ldapsearch -x -H ldap://<IP> -D '<USER>@<DOMAIN>' -w '<PASSWORD>' \
  -b 'CN=Deleted Objects,DC=<DOMAIN>,DC=<TLD>' \
  -E '!1.2.840.113556.1.4.417=::/' \
  '(objectClass=*)' name sAMAccountName
```

## Variants

- **Recycle Bin not enabled**: tombstones keep only `objectSid`, `sAMAccountName`, `lastKnownParent`, `whenCreated` and little else. "Reanimating" the object by flipping `isDeleted` works, but almost everything else is lost.
- **`msDS-deletedObjectLifetime`**: 180 days by default with Recycle Bin; once it expires the object is really deleted. A value of 0 means it never expires, which makes the risk permanent.
- **Deleted service accounts**: restoring them brings back SPNs and permissions, not just the password.
- **Defensive side**: the AD recycle bin is also the correct way to recover an accidental deletion, so restricting it has an operational cost; auditing offsets that.

## Hardening

- Disable and rotate the password before deleting any account, especially privileged ones.
- Clear sensitive attributes (`description`, `info`, custom attributes) before deletion.
- Limit the **AD Recycle Bin** group to named administrative accounts with MFA and auditing, never service accounts.
- Lower `msDS-deletedObjectLifetime` where policy allows, and review custom attributes that store secrets.

## Detection

- **4662** on directory objects for read access to `Deleted Objects`, and LDAP queries carrying the `1.2.840.113556.1.4.417` control.
- **4688** (or Sysmon 1) with `Get-ADObject -includeDeletedObjects` or `Restore-ADObject` on the command line.
- Event **4780** / privileged group change auditing if an account is added to `AD Recycle Bin`.
- On the DC, anonymous or service-account queries to the `CN=Deleted Objects` container outside business hours.

MITRE: T1087.002 (domain account discovery), T1078.002 (domain accounts), T1098 (account manipulation), T1552.001 (credentials in files).

## References

- <https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/get-started/adac/active-directory-recycle-bin>
- <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/1e3974d4-3c3d-4a49-9c9a-3f0e0e3fbe8a>
- <https://attack.mitre.org/techniques/T1098/>
- <https://www.hackthebox.com/machines/cascade>
