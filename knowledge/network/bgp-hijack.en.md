---
topic: BGP — route hijacking and traffic capture
tags: [network, bgp, routing, mitm, ftp]
---

# BGP — route hijacking and traffic capture

[🇪🇸 Español](bgp-hijack.md) | **English**

## Concept

BGP exchanges prefixes between autonomous systems without authentication by default. A compromised router can announce a more specific prefix than the legitimate one; neighbors prefer that route and the host's traffic crosses the attacker, who can capture or modify it.

## When it applies

- A router with an established BGP session is controlled.
- The neighbor accepts announcements without RPKI or prefix filters.
- Interesting traffic (FTP, HTTP, SMTP) crosses that router.

## Procedure

1. Review neighbors, prefixes and tables with `show ip bgp summary`.
2. Announce a `/32` or more specific prefix toward the target host.
3. Confirm the route changes in the router table.
4. Capture traffic with `tcpdump` or redirect it to a listener.

```bash
router bgp 65001
 network 10.10.10.0 mask 255.255.255.0
 neighbor 10.10.10.1 remote-as 65000
```

```bash
tcpdump -i any -nn -A 'tcp port 21'
```

## Variants

- Announce the FTP server prefix to steal credentials.
- Redirect DNS or HTTP to a controlled server.
- Use a more specific prefix than the original announcement.

## Limitations

- RPKI, BGPsec or prefix filters block the announcement.
- The session should use MD5 or TCP-AO authentication.
- Traffic may be encrypted (FTPS, HTTPS).

## Mitigation

- Sign routes with RPKI and BGPsec.
- Filter prefixes and use max-prefix.
- Authenticate BGP sessions and monitor route changes.

## Detection

- New announcements of more specific prefixes.
- Next-hop changes without maintenance.
- Latency drops or asymmetric traffic.

## References

- [RFC 4271 — BGP](https://www.rfc-editor.org/rfc/rfc4271)
- [0xdf — Carrier](https://0xdf.gitlab.io/2019/03/16/htb-carrier.html)
- [MITRE ATT&CK — T1557](https://attack.mitre.org/techniques/T1557/)
