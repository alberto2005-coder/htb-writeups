---
topic: SNMP enumeration
tags: [windows, snmp, enumeration, credentials, network]
---

# SNMP enumeration

**English** | [🇪🇸 Español](snmp-enumeration.md)

## Concept

SNMP exposes management information (interfaces, processes, software, users and sometimes credentials) when it uses weak communities or unauthenticated versions. On Windows, the service may reveal hostnames, domains, accounts and configuration strings.

## When it applies

- Port 161/UDP open.
- `public`/`private` community or SNMPv1/v2c.
- Network devices, printers or Windows servers with SNMP enabled.

## Requirements

1. Target IP and UDP connectivity.
2. `snmpwalk`/`snmp-check`/`onesixtyone`.
3. Community wordlist.

## Procedure

```bash
onesixtyone -c communities.txt <IP>
snmpwalk -v2c -c public <IP> 1.3.6.1.2.1
snmpwalk -v2c -c public <IP> 1.3.6.1.4.1
```

Review system, process, installed-software and user OIDs. Configuration strings may include paths, domains and passwords.

```bash
snmp-check <IP> -c public
```

On Windows, MIB `1.3.6.1.2.1.25` exposes hardware and software; enterprise OIDs may contain proprietary configuration.

## Variants

- **SNMPv1/v2c**: cleartext community.
- **SNMPv3**: requires a user and authentication; try `noAuthNoPriv`.
- **Trap receiver**: listen for traps to discover devices.
- **Windows SNMP**: management extension with process information.

## Limitations

- UDP may be filtered.
- The community may be non-standard.
- SNMPv3 with `authPriv` cannot be enumerated without credentials.
- Information may be stale.

## Mitigation

- Disable SNMP when unnecessary.
- Use SNMPv3 with `authPriv`.
- Change default communities and apply ACLs.
- Never store secrets in OIDs.

## Detection

- `snmpwalk` queries from unauthorised hosts.
- Spikes in UDP/161 traffic.
- Attempts with common communities.
- Access to configuration/credential OIDs.

MITRE ATT&CK: T1046 (Network Service Discovery), T1552 (Unsecured Credentials).

## References

- <https://www.net-snmp.org/>
- <https://attack.mitre.org/techniques/T1046/>
- <https://book.hacktricks.xyz/network-services-pentesting/pentesting-snmp>
