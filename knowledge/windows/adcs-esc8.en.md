# AD CS ESC8 — NTLM Relay to Web Enrollment

**English** | [🇪🇸 Español](adcs-esc8.md)

## Overview

ESC8 is an Active Directory Certificate Services (AD CS) abuse condition in which an HTTP Certificate Authority Web Enrollment endpoint (or equivalent web enrollment service) accepts NTLM authentication and can be targeted by an NTLM relay. Rather than learning the victim's password or cracking an NTLM hash, an operator induces an NTLM authentication to a controlled listener and relays the exchange to the vulnerable enrollment endpoint.

Impact depends on enrollment permissions, available certificate templates, and the identity whose authentication is relayed. In a domain, relaying a privileged account's authentication may allow enrollment of a certificate usable to authenticate as that account.

> Test only in systems you own or environments for which you have explicit authorization.

## Preconditions

- AD CS is deployed and an HTTP Web Enrollment endpoint is reachable.
- The endpoint accepts NTLM and lacks effective relay protections.
- A victim can be induced to authenticate to an operator-controlled destination.
- The CA and templates permit issuance of a certificate suitable for the requested identity.
- The relayed identity has sufficient enrollment permissions.

The mere presence of AD CS does not prove ESC8. Verify authentication protocol, transport, endpoint protections, and enrollment permissions.

## Conceptual workflow

1. Identify the CA and published enrollment endpoints.
2. Within the authorized scope, determine whether the endpoint accepts NTLM over HTTP and which protections are enforced.
3. Establish which identity could authenticate and which templates it can enroll in.
4. Assess whether the authentication flow can be relayed to the enrollment service.
5. If issuance is possible, validate certificate use in the lab.
6. Record the affected identity, permissions, template, CA, evidence, and missing controls.

## Enumeration and review

Common inventory and audit sources include:

- `certutil -config - -ping` to discover or test known CAs.
- Certipy (for example, `certipy find`) to inventory CAs, templates, and AD CS configuration.
- BloodHound/SharpHound and LDAP queries to understand groups, ACLs, and enrollment rights.
- IIS review: bindings, Windows Authentication, NTLM, and Extended Protection for Authentication (EPA).

Record at least:

- Endpoint FQDN and enrollment paths.
- HTTP versus HTTPS and TLS configuration.
- Enabled authentication providers.
- EPA/channel-binding status and signing requirements.
- Published templates, EKUs, enrollment rights, subject/SAN supply, and approval requirements.
- CA service identity and permissions.

## Mitigation

- Disable NTLM on enrollment endpoints where feasible and prefer Kerberos.
- Require HTTPS and correctly configure Extended Protection for Authentication (EPA).
- Enforce channel binding and NTLM relay protections in IIS/services that support them.
- Disable Web Enrollment if it is not required.
- Restrict enrollment on sensitive templates; review EKUs, subject/SAN supply, and approval controls.
- Reduce HTTP exposure and segment AD CS servers.
- Audit and monitor certificate requests, especially unexpected requests for privileged identities.
- Follow current Microsoft guidance for AD CS, IIS, and NTLM.

HTTPS alone does not guarantee relay protection: EPA/channel binding and the service's authentication behavior must also be reviewed.

## Detection and response

- Correlate CA certificate-issuance events (including AD CS audit events enabled in the environment).
- Look for unusual requests, sensitive templates, unexpected requesters, and atypical SAN/UPN values.
- Review IIS logs for enrollment paths, NTLM authentication, and anomalous patterns.
- Investigate privileged-account authentication from unexpected hosts.
- If abuse is suspected, identify and revoke improperly issued certificates, assess derived sessions, and rotate credentials where appropriate.

## Related concepts

- **NTLM relay** is the general technique of forwarding NTLM authentication to another service.
- **ESC8** is a specific AD CS scenario where a web enrollment endpoint can be the relay target.
- **ESC1** concerns templates that let an enrollee specify an identity in a certificate; it is not the same as ESC8.
- **Shadow Credentials** changes authentication material associated with an account; it is different from enrolling a certificate through Web Enrollment.

## Audit checklist

- [ ] Is Web Enrollment or another HTTP enrollment endpoint present?
- [ ] Does it accept NTLM?
- [ ] Is HTTPS enforced?
- [ ] Is EPA/channel binding enabled and validated?
- [ ] Can NTLM be disabled for the service?
- [ ] Which templates and enrollment permissions are available?
- [ ] Are certificate issuances audited and reviewed?
- [ ] Is there a revocation and incident-response process?

## References

- Microsoft Learn — Certificate Authority Web Enrollment: https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/certificate-authority-web-enrollment
- Microsoft Learn — Extended Protection for Authentication: https://learn.microsoft.com/en-us/dotnet/framework/wcf/feature-details/extended-protection-for-authentication-overview
- SpecterOps — Certified Pre-Owned: https://specterops.io/wp-content/uploads/sites/3/2022/06/Certified_Pre-Owned.pdf
- Certipy: https://github.com/ly4k/Certipy
