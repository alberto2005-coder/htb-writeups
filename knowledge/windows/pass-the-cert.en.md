# PassTheCert

**English** | [🇪🇸 Español](pass-the-cert.md)

## Overview

PassTheCert is a certificate-based authentication abuse technique in Active Directory. When an operator has a valid certificate and its private key for an identity, certain AD services may accept certificate authentication (for example, TLS client authentication to LDAP/LDAPS). The identity can then perform operations allowed by its permissions without requiring its password.

PassTheCert is not a single vulnerability, and not every certificate can authenticate to every service. The outcome depends on the certificate, identity mapping, domain configuration, target service, and authentication policies.

> Use only in lab domains or authorized assessments.

## Key concepts

- **Certificate:** contains a public key and attributes/identifiers that may be mapped to an account.
- **Private key:** proves possession of the associated cryptographic identity.
- **Schannel / TLS client authentication:** a mechanism some Windows services can use to authenticate clients with certificates.
- **LDAP/LDAPS:** may accept certificate-based authentication when the domain controller and client are configured for it.
- **AD permissions:** successful authentication does not grant additional privileges by itself; allowed operations depend on the account's ACLs and group memberships.

## Requirements

- A certificate valid for the domain authentication context.
- Access to the corresponding private key.
- A service that supports and trusts certificate-based authentication.
- A valid certificate-to-account mapping under the current configuration and mapping method.
- Sufficient AD permissions for the action being assessed.

## Assessment workflow

1. Identify how the certificate was obtained and which identity it represents.
2. Verify validity, trust chain, EKU, SAN/UPN, and private-key availability.
3. Determine whether the target service supports TLS client-certificate authentication.
4. Check the certificate mapping method enforced by domain controllers.
5. In a lab, validate authentication to LDAP/LDAPS and confirm the resulting identity.
6. Assess only operations allowed by that account's privileges.
7. Document the certificate, identity, service, mapping method, and observed permissions.

## Tools and context

- Certipy: AD CS inventory and assessment; some features depend on version and scenario.
- OpenSSL: inspect certificates and keys in supported formats.
- `certutil`: inspect and manage certificates on Windows.
- LDAP tools: validate directory connectivity, TLS, and permissions.
- PassTheCert (project/tool): consult the current documentation and version before use; arguments and capabilities may change.

Do not copy commands from a guide without checking the version, certificate format, mapping method, and service compatibility.

## Related techniques

- **Pass-the-Certificate / PassTheCert:** uses a certificate and its private key to authenticate to a compatible service.
- **PKINIT:** a Kerberos extension enabling public-key-based initial authentication; it is not identical to LDAP TLS certificate authentication.
- **Shadow Credentials:** modifies account attributes to register public-key material used for authentication, often associated with PKINIT.
- **AD CS ESC8:** abuses NTLM relay against Web Enrollment to obtain a certificate; PassTheCert may be a later stage if the issued certificate supports authentication.
- **Pass-the-Hash:** uses NTLM material, not an X.509 certificate.

## Mitigation and hardening

- Secure AD CS and templates: restrict enrollment rights, EKUs, subject/SAN supply, and approval settings.
- Protect private keys; avoid unnecessary exportability and enforce strong access controls.
- Maintain a trusted PKI and revoke compromised or unnecessary certificates.
- Review and harden certificate-to-account mapping according to current Microsoft guidance, especially following security changes to certificate-based authentication.
- Keep Windows systems updated and configure recommended enforcement modes.
- Audit certificate-based authentication and changes to mapping attributes.
- Reduce privileges and review ACLs on sensitive AD objects.

## Detection and response

- Review Kerberos/Schannel/LDAP authentication events available for the environment's Windows version and configuration.
- Investigate certificate-based authentication from unusual systems or locations.
- Correlate certificate issuer, serial number, thumbprint, and SAN/UPN with the authenticated account.
- Review recent changes to certificate mapping attributes and AD CS issuance activity.
- If a private key is compromised, revoke the certificate, locate copies, and assess subsequent use of the identity.

## Checklist

- [ ] What is the certificate's source and owner?
- [ ] Is the private key available and protected?
- [ ] Are the trust chain and EKU appropriate?
- [ ] Which certificate mapping method is configured?
- [ ] Does the service accept client-certificate authentication?
- [ ] What permissions does the mapped account have?
- [ ] Are authentication and mapping changes audited?
- [ ] Is there a revocation process for compromised certificates?

## References

- Microsoft Learn — consult current documentation for certificate-based authentication and strong certificate mapping: https://learn.microsoft.com/en-us/windows-server/security
- Microsoft Support — KB5014754, certificate-based authentication changes: https://support.microsoft.com/help/5014754
- PassTheCert: https://github.com/AlmondOffSec/PassTheCert
- Certipy: https://github.com/ly4k/Certipy
