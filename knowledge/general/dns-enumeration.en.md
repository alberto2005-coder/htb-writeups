---
topic: DNS enumeration
tags: [general, dns, enumeration, zone-transfer, subdomains, recon]
---

# DNS enumeration

**English** | [🇪🇸 Español](dns-enumeration.md)

## Concept

DNS reveals hostnames, internal services, mail and subdomains. Enumeration looks for misconfigured zone transfers, wildcard records, forgotten subdomains and TXT records containing sensitive information.

## When it applies

- A domain with exposed NS or MX records.
- An authoritative DNS server reachable.
- An application using virtual hosts.
- Certificate transparency entries with subdomains.

## Procedure

1. Query NS, MX and TXT.
2. Attempt a zone transfer.
3. Enumerate subdomains and compare responses.
4. Resolve internal hosts and ranges.
5. Cross-reference certificates and OSINT.

```bash
dig +short NS <DOMAIN>
dig +short MX <DOMAIN>
dig AXFR <DOMAIN> @<NAMESERVER>
dnsrecon -d <DOMAIN> -t std,brt
```

## Variants

- Full zone transfer.
- Wildcard DNS hiding real subdomains.
- TXT records with verification tokens.
- Internal DNS reachable through a VPN or pivot.

## Limitations

- Zone transfers are usually disabled.
- Subdomains may not resolve publicly.
- Wildcards produce false positives.
- DNS may be segmented.

## Mitigation and detection

- Restrict `AXFR` to authorised secondary servers.
- Audit records and remove stale entries.
- Monitor bulk queries and transfers.
- Review certificates and TXT records regularly.

## References

- <https://www.rfc-editor.org/rfc/rfc1035>
- <https://attack.mitre.org/techniques/T1590/002/>
- <https://book.hacktricks.wiki/en/network-services-pentesting/pentesting-dns.html>
