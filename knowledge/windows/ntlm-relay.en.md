# NTLM Relay

**English** | [🇪🇸 Español](ntlm-relay.md)

## Overview

NTLM relay is a technique in which an intermediary forwards an NTLM authentication exchange in real time between a victim and a target service. The operator does not need the plaintext password or to crack the hash: the attack relies on the target accepting relayed authentication and on missing protections such as SMB signing, LDAP signing/channel binding, or Extended Protection for Authentication (EPA), depending on the protocol.

It is not the same as **capturing and cracking NTLM hashes**. In a relay, the exchange is forwarded to another service; a reusable hash is not necessarily obtained.

> Use only in labs and authorized assessments.

## Components and prerequisites

- An identity that initiates NTLM authentication.
- A service to which that identity connects or is induced to connect.
- A target that accepts NTLM without adequately validating connection integrity/channel binding.
- An operation allowed by the authenticated identity's privileges.

Targets and impact vary: SMB, LDAP/LDAPS, HTTP, AD CS Web Enrollment, and other compatible services. Different protocols expose different operations.

## Conceptual workflow

1. Identify services that accept NTLM and inspect their configured protections.
2. Identify legitimate or induced paths through which an account may authenticate.
3. In a lab, assess whether the exchange can be relayed to the target service.
4. Determine which operations the identity is allowed to perform on that service.
5. Validate impact with a harmless action and document the conditions.
6. Fix the configuration and repeat the defensive validation.

## Common attack surfaces

| Target | Relevant controls | Risk when missing |
|---|---|---|
| SMB | SMB signing, NTLM restrictions | Relay to vulnerable SMB services |
| LDAP | LDAP signing, channel binding, correctly configured LDAPS | LDAP operations as the relayed identity |
| HTTP/IIS | HTTPS, EPA, channel binding, authentication settings | Relay to web applications or Web Enrollment |
| AD CS Web Enrollment | NTLM, EPA, enrollment rights and templates | Certificate issuance (related to ESC8) |

LDAPS or HTTPS should not automatically be considered immune: protection depends on channel validation, EPA, and the actual service configuration.

## Enumeration and audit

- Inventory where NTLM is used and where it can be disabled.
- Review domain and local security policies related to LAN Manager/NTLM.
- Check SMB signing on clients and servers.
- Review LDAP signing and LDAP channel binding on domain controllers.
- Review IIS Windows Authentication and EPA on web applications.
- Use inventory tools such as `ntlmrelayx` only in authorized labs to validate controls, never to operate against third-party networks.
- Correlate NTLM authentications with source host, account, service, and timestamp.

## Mitigation

- Reduce and, where feasible, disable NTLM; migrate to Kerberos.
- Require SMB signing on servers and clients.
- Require LDAP signing and configure LDAP channel binding according to environment compatibility.
- Configure EPA on IIS and compatible services.
- Use HTTPS/LDAPS correctly, with certificate validation and channel binding.
- Restrict inter-segment traffic and limit which systems can reach authentication services.
- Disable unnecessary legacy services and prevent privileged accounts from logging on to untrusted workstations.
- Apply Windows policies to restrict NTLM gradually, monitoring before enforcing blocks.

## Detection

- Audit NTLM events on domain controllers and endpoints; review available logs according to Windows version and audit policy.
- Correlate the same account authenticating from unexpected hosts or to multiple services within unusual time windows.
- Look for NTLM authentication from servers that do not normally act as clients.
- Monitor sensitive LDAP changes, object creation/modification, and certificate requests.
- Do not rely on a single event: correlate identity, source, destination, protocol, and operation.

## NTLM Relay vs. Pass-the-Hash

- **NTLM Relay:** forwards an active authentication exchange to another service.
- **Pass-the-Hash:** uses NTLM hash material as a credential to authenticate where the protocol and environment permit it.
- **NetNTLM capture:** obtains a challenge/response that may be subjected to offline cracking; it is not synonymous with relay.

## Defensive checklist

- [ ] Where is NTLM still enabled?
- [ ] Is SMB signing required?
- [ ] Is LDAP signing required?
- [ ] Is LDAP channel binding configured?
- [ ] Do IIS and other web services enforce EPA?
- [ ] Are privileged accounts protected against coerced authentication?
- [ ] Are NTLM authentications and sensitive operations monitored?
- [ ] Is there a phased, tested NTLM-reduction plan?

## References

- Microsoft Learn — Restrict NTLM: https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/security-policy-settings/network-security-restrict-ntlm-ntlm-authentication-in-this-domain
- Microsoft Learn — LDAP signing: https://learn.microsoft.com/en-us/troubleshoot/windows-server/active-directory/enable-ldap-signing-in-windows-server
- Microsoft Learn — SMB signing: https://learn.microsoft.com/en-us/windows-server/storage/file-server/smb-signing
- Impacket: https://github.com/fortra/impacket
- SpecterOps — Certified Pre-Owned: https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf
