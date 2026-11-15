---
topic: SNMP and credential leaks
tags: [linux, snmp, credentials, enumeration]
---

# SNMP and credential leaks

[🌐 Español](snmp-community-credential-leak.md) | **English**

## Concept

SNMP can expose much more than metrics: hostnames, processes, scripts and additional community strings. A read community with broader access can reveal API or service credentials.

## When it applies

- `161/udp` responds.
- The `public` community returns information.
- An additional community such as `internal` exists.

## Procedure

1. Enumerate with `snmpwalk` and `public`.
2. Try common communities with `snmpbrute.py`.
3. Walk OIDs with the discovered community.
4. Look for strings, scripts and credentials.

```bash
snmpwalk -v2c -c public <IP>
python3 snmpbrute.py -t <IP>
snmpwalk -v2c -c internal <IP>
```

## Variants

- Use SNMPv3 with a bootstrap user.
- Read `snmpd.conf` after local access.
- Combine with API credentials.

## Limitations

- SNMP must be exposed.
- The community must have permissions.
- The network may filter UDP/161.

## Mitigation and detection

- Use SNMPv3 and strong communities.
- Restrict SNMP to the management network.
- Do not store credentials in SNMP-readable scripts.

## References

- <https://www.net-snmp.org/docs/man/snmpd.conf.html>
- <https://owasp.org/www-community/attacks/SNMP_Injection>
- <https://attack.mitre.org/techniques/T1046/>
