---
topic: SNMP and IPv6 — discovering hidden services
tags: [linux, snmp, ipv6, discovery, command-injection]
---

# SNMP and IPv6 — discovering hidden services

**English** | [🌐 Español](snmp-ipv6-discovery.md)

## Concept

SNMP exposes interfaces, processes and system tables, including IPv6 addresses. A service may listen only on IPv6 and stay outside an IPv4 scan. `snmpwalk` reveals the address and port; the service usually has the same vulnerable surface as its IPv4 equivalent but less filtering.

## When it applies

- SNMP responds with default communities.
- An IPv4 scan misses expected services.
- The application or system has IPv6 interfaces.

## Procedure

1. Enumerate SNMP and review interfaces and processes.
2. Extract IPv6 addresses and ports.
3. Access the service over IPv6 with `curl -g` or the right client.
4. Exploit the service vulnerability.

## Commands

```bash
snmpwalk -v2c -c public <IP>
snmpwalk -v2c -c public <IP> ipAddresses
snmpwalk -v2c -c public <IP> tcpConnTable
curl -g -6 "http://[<IPv6>]/index.php?cmd=id"
```

## Variants

- Use `snmp-check` for a summary.
- Enumerate processes with `hrSWRunTable`.
- Combine with `nmap -6` if the host is reachable.

## Limitations

- The community must be valid.
- IPv6 may not be reachable from the attacker.
- The service may be firewall-filtered.

## Mitigation

- Change communities and restrict SNMP.
- Apply the same filtering to IPv6 as IPv4.
- Inventory services listening on all interfaces.

## Detection

- `snmpwalk` from unauthorized hosts.
- Queries to interface and process tables.
- Access to uninventoried IPv6 services.

## References

- [0xdf — Mischief](https://0xdf.gitlab.io/2019/01/05/htb-mischief.html)
- [Net-SNMP — snmpwalk](http://www.net-snmp.org/docs/man/snmpwalk.html)
- [CWE-200 — Exposure of Sensitive Information](https://cwe.mitre.org/data/definitions/200.html)
