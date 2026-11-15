---
topic: Active Directory discovery over IPv6
tags: [windows, ad, ipv6, rpc, discovery]
---

# Active Directory discovery over IPv6

[🌐 Español](ipv6-ad-discovery.md) | **English**

## Concept

A host may filter AD ports on IPv4 while still exposing them on IPv6. RPC can return the DC's IPv6 address, and scanning it reveals DNS, Kerberos, LDAP, SMB and WinRM.

## When it applies

- IPv4 only shows HTTP and RPC.
- The RPC endpoint answers `IOXIDResolver`.
- The network allows IPv6 traffic.

## Procedure

1. Query the DC interfaces over RPC.
2. Parse the response and extract the IPv6 address.
3. Scan all ports on that address.
4. Use the domain name and update `/etc/hosts`.

```bash
python3 IOXIDResolver.py -t <IP>
nmap -6 -p- --min-rate 10000 <IPv6>
nmap -6 -sCV -p53,88,389,445,5985 <IPv6>
```

## Variants

- Use `rpcclient` or `impacket` to query interfaces.
- Discover the DC through DNS and try its IPv6.
- Scan only common AD ports if a full scan is slow.

## Limitations

- The network must route IPv6.
- The firewall may filter IPv6 too.
- The RPC response may require null credentials.

## Mitigation and detection

- Filter IPv6 with the same rules as IPv4.
- Disable IPv6 when it is not needed.
- Audit RPC and interface discovery.

## References

- <https://learn.microsoft.com/en-us/windows/win32/rpc/rpc-start-page>
- <https://attack.mitre.org/techniques/T1016/>
- <https://0xdf.gitlab.io/2021/04/10/htb-apt.html>
