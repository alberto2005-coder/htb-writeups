---
topic: Kerberos — keytabs and SSH authentication
tags: [linux, kerberos, keytab, ssh, privesc]
---

# Kerberos — keytabs and SSH authentication

**English** | [🌐 Español](kerberos-keytab.md)

## Concept

A keytab contains the keys of a Kerberos principal and obtains tickets without a password. If found in a backup or accessible directory, it can be used with `kinit -kt` to authenticate as that user. SSH with GSSAPI accepts the ticket and grants access without knowing the password.

## When it applies

- A `.keytab` file is accessible or in a backup.
- SSH has `GSSAPIAuthentication yes`.
- The Kerberos service is reachable.

## Procedure

1. Locate and copy the keytab.
2. List its entries with `klist -kt`.
3. Obtain a ticket with `kinit -kt`.
4. Connect over SSH with `-K` and the matching user.

## Commands

```bash
find / -name "*.keytab" 2>/dev/null
klist -kt <FILE>.keytab
kinit -kt <FILE>.keytab <USER>
klist
ssh -K <USER>@<HOST>
```

## Variants

- Use a service account keytab for Kerberoasting.
- Extract hashes with `keytabextract`.
- Combine with `impacket` to obtain a TGT.

## Limitations

- The keytab must belong to a valid account.
- Clocks must be synchronized.
- SSH must allow GSSAPI and the user must exist.

## Mitigation

- Protect keytabs and rotate keys periodically.
- Restrict SSH GSSAPI to required accounts.
- Do not include keytabs in accessible backups.

## Detection

- Keytab reads outside services.
- Kerberos tickets issued to service accounts.
- SSH GSSAPI connections from unusual hosts.

## References

- [MIT Kerberos — keytab](https://web.mit.edu/kerberos/krb5-latest/doc/basic/keytab_def.html)
- [0xdf — Tentacle](https://0xdf.gitlab.io/2021/06/19/htb-tentacle.html)
- [CWE-522 — Insufficiently Protected Credentials](https://cwe.mitre.org/data/definitions/522.html)
