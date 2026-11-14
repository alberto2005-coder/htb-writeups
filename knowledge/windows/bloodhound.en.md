---
topic: BloodHound
tags: [windows, active-directory, bloodhound, sharphound, acl, attack-path]
---

# BloodHound

**English** | [🇪🇸 Español](bloodhound.md)

## Concept

BloodHound models users, groups, computers, sessions and Active Directory ACLs as a graph. It finds privilege paths —Kerberoasting, delegation, ESC, `GenericAll`, `WriteDacl`— and prioritises lateral movement.

## When it applies

- An enumerable Active Directory domain.
- User or computer credentials.
- A search for paths to Domain Admin.
- ACL and session analysis.

## Procedure

1. Collect data with SharpHound or `bloodhound-python`.
2. Import the ZIP into BloodHound.
3. Review users with privileged sessions.
4. Search for paths to Domain Admin.
5. Validate permissions before exploiting.

```bash
bloodhound-python -u <USER> -p '<PASSWORD>' -ns <DC> -d <DOMAIN> -c All
# Import the ZIP into the BloodHound UI
```

## Variants

- `All` or `DCOnly` collection.
- ACL, delegation and GPO analysis.
- Sessions and credentials on computers.
- Paths to ADCS and service accounts.

## Limitations

- Collection can be noisy.
- Data may be incomplete.
- A visible path is not always exploitable.
- Collector and server versions must match.

## Mitigation and detection

- Audit ACLs and privileged sessions.
- Apply tiering and PAWs.
- Monitor bulk LDAP queries.
- Remove unnecessary paths and permissions.

## References

- <https://bloodhound.readthedocs.io/>
- <https://github.com/dirkjanm/BloodHound.py>
- <https://attack.mitre.org/techniques/T1087/002/>
