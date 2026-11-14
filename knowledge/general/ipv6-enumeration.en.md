---
topic: IPv6 enumeration
tags: [general, ipv6, snmp, enumeration, ssh]
---

# IPv6 enumeration

[🌐 Español](ipv6-enumeration.md) | **English**

## Concept

A host may expose services only over IPv6. SNMP, DNS or traffic can reveal `dead:beef::/64` or link-local addresses. Incomplete IPv4 enumeration misses SSH, HTTP or internal panels.

## When it applies

- `nmap` shows only port 80 on IPv4.
- SNMP responds with the interface table.
- The host has a documented or predictable IPv6 prefix.

## Procedure

1. Enumerate SNMP and the address table.
2. Extract the prefix and suffix.
3. Scan IPv6 with `nmap -6`.
4. Try SSH/HTTP against the discovered address.

```bash
snmpwalk -v2c -c public <IP> 1.3.6.1.2.1.4.34
nmap -6 -p22,80 dead:beef::<SUFFIX>
ssh -6 user@dead:beef::<SUFFIX>
```

## Variants

- Multicast DNS (`ff02::fb`).
- Router advertisements to discover prefixes.
- DNS AAAA for vhosts.
- 6to4 or Teredo tunnels.

## Limitations

- The address may change or require a specific interface.
- A firewall may filter ICMPv6 and break connectivity.
- Not every client supports `-6` or `ssh -6`.

## Mitigation and detection

- Inventory IPv6 addresses and services.
- Filter SNMP and limit exposure to the internal network.
- Apply the same firewall rules as IPv4.
- Alert on scans and SSH over uninventoried IPv6.

## References

- <https://www.rfc-editor.org/rfc/rfc4291>
- <https://nmap.org/book/scan-methods-ipv6.html>
- <https://attack.mitre.org/techniques/T1046/>
