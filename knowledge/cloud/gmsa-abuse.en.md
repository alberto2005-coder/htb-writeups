---
topic: gMSA abuse
tags: [windows, active-directory, gmsa, kerberos, dacl, credential-access]
---

# gMSA abuse

**English** | [🇪🇸 Español](gmsa-abuse.md)

## Concept

A group Managed Service Account (gMSA) is a service account whose NTLM hash is managed by Active Directory and rotated automatically. The password derives from a KDS root key and can be recovered if the attacker controls `msDS-GroupMSAMembership` or an equivalent right that allows reading it.

## When it applies

- Enumerating service accounts in a domain.
- A non-admin user with `WriteProperty` over a gMSA.
- Lateral movement from a service account.
- Chains involving `gMSA_Managers` or `PrincipalsAllowedToRetrieveManagedPassword`.

## Requirements and conditions

- Authenticated domain access.
- Permission to modify gMSA membership or ability to read it.
- Tools such as `BloodHound`, `certipy`, `impacket` or `netexec`.
- DC connectivity and synchronised time.

## Procedure

1. Enumerate gMSAs and their permissions.
2. Identify who can write `msDS-GroupMSAMembership`.
3. Add the controlled account as an authorised principal.
4. Retrieve the gMSA NTLM hash.
5. Use the hash for Kerberos or resource access.

```bash
nxc smb dc01.haze.htb -u <USER> -p '<PASSWORD>' --gmsa
python3 certipy-ad shadow auto -username '<GMSA>$@<DOMAIN>' -hashes :<NTLM> -account <TARGET>
```

## Variants

- Standard gMSA with a KDS root key.
- dMSA in newer domains.
- Abuse through `WriteOwner` and `WriteMembers` on an intermediate group.
- Hash use for Pass-the-Hash or TGT requests.

## Limitations

- Without permission over the gMSA, the password is not obtainable.
- Rotation invalidates the hash after a period.
- Some environments require Kerberos and exact time.
- The path may depend on intermediate ACLs.

## Mitigation

- Audit who can modify `msDS-GroupMSAMembership`.
- Restrict `gMSA_Managers` and `WriteProperty` rights.
- Use administrative tiering and PAWs.
- Monitor ACL and group changes.

## Detection

- Alert on `msDS-GroupMSAMembership` changes.
- Detect gMSA reads from unauthorised hosts.
- Review events 4662 and 5136 on service objects.
- Correlate authentications from unusual service accounts.

## References

- <https://learn.microsoft.com/en-us/windows-server/security/group-managed-service-accounts/group-managed-service-accounts-overview>
- <https://adsecurity.org/?p=2011>
- <https://attack.mitre.org/techniques/T1558/003/>
- <https://bloodhound.readthedocs.io/>
