---
topic: Active Directory — UPN spoofing across Windows and Linux
tags: [windows, active-directory, kerberos, upn, sssd, privesc]
---

# Active Directory — UPN spoofing across Windows and Linux

**English** | [🌐 Español](upn-spoofing.md)

## Concept

Windows and Linux resolve `userPrincipalName` differently. If the UPN of a controlled account can be written and a TGT is requested with `NT_ENTERPRISE`, a Linux host may authenticate it as another account with the same UPN, such as an `.adm` account.

## When it applies

- A controlled account can change its UPN or has `GenericWrite`.
- A privileged account has a known UPN.
- The Linux host uses SSSD/Kerberos with `use_fully_qualified_names=False`.

## Procedure

1. Enumerate UPNs and `.adm` accounts.
2. Set the controlled account's UPN to the admin UPN.
3. Request a TGT with `principalType=NT_ENTERPRISE`.
4. Use the ticket on the Linux host and restore the UPN.

## Commands

```bash
bloodyAD --host dc-01 -d darkcorp.htb -u john.w -p '<PASS>' set object angela.w userPrincipalName angela.w.adm
# request a TGT with NT_ENTERPRISE and use the ccache on the Linux host
klist
```

## Variants

- Change a UPN through `GenericWrite` over another account.
- Combine with shadow credentials to get the password.
- Use `getTGT.py` or Rubeus with `enterprise`.

## Limitations

- The host must trust the UPN for account mapping.
- A cleanup reverts the UPN and it must be reapplied.
- Kerberos may reject the ticket if the SPN does not match.

## Mitigation

- Monitor `userPrincipalName` changes.
- Do not use UPN as a unique identifier on Linux.
- Set `use_fully_qualified_names=True` and review SSSD.

## Detection

- UPN changes followed by an `NT_ENTERPRISE` TGT.
- Linux logins with an admin UPN.
- Anomalous 4768/4769 events for the account.

## References

- [0xdf — DarkCorp](https://0xdf.gitlab.io/2025/10/18/htb-darkcorp.html)
- [Pen Test Partners — A broken marriage](https://www.pentestpartners.com/security-blog/a-broken-marriage-abusing-mixed-vendor-kerberos-stacks/)
- [Microsoft — userPrincipalName](https://learn.microsoft.com/en-us/windows/win32/adschema/a-userprincipalname)
