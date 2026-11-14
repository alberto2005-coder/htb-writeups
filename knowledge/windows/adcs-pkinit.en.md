---
topic: ADCS, PKINIT y plantillas vulnerables
tags: [windows, active-directory, adcs, pkinit, certificates, esc1]
---

# ADCS, PKINIT and Vulnerable Templates

**English** | [🇪🇸 Español](adcs-pkinit.md)

## Concept

Active Directory Certificate Services issues certificates for authentication. A template allowing the requester to specify the subject and a smart-card EKU can become a certificate for any user. PKINIT uses that certificate to obtain a TGT.

## When it applies

- ADCS installed and templates published.
- Enrolment rights for a domain user.
- Template with `ENROLLEE_SUPPLIES_SUBJECT` and an authentication EKU.

## Procedure

1. Enumerate the CA and templates.
2. Look for controllable subject and a suitable EKU.
3. Request the certificate with the target `upn`.
4. Convert the PFX to PKINIT format.
5. Obtain and use the TGT.

```bash
certipy-ad find -u <USER>@<DOMAIN> -p <PASS> -dc-ip <DC>
certipy-ad req -u <USER>@<DOMAIN> -p <PASS> -ca <CA> -template <TEMPLATE> -upn administrator@<DOMAIN>
```

## Variants

- ESC1 (controllable subject).
- ESC2/ESC3 (EKU and enrolment agents).
- ESC8 (HTTP relay to ADCS).

## Limitations

- The template must allow enrolment.
- The EKU must support authentication.
- Patches and auditing may block ESC1.

## Mitigation

- Review template permissions and EKUs.
- Disable `ENROLLEE_SUPPLIES_SUBJECT` unless required.
- Require approval and audit issuance.
- Protect enrolment traffic.

## Detection

- Requests with another user's `upn`.
- Off-hours issuance.
- Unusual PKINIT authentication.

## References

- <https://posts.specterops.io/certified-pre-owned-d95910965cd2>
- <https://github.com/ly4k/Certipy>
- <https://attack.mitre.org/techniques/T1649/>
