---
topic: ARP and DNS poisoning
tags: [forensics, arp, dns, spoofing, pcap, mitm, layer2]
---

# ARP and DNS poisoning

**English** | [🇪🇸 Español](arp-dns-poisoning.md)

## Concept

ARP has no authentication: a host can announce that the gateway IP belongs to its MAC. If it succeeds, traffic flows through the attacker. With forged DNS, victims resolve legitimate domains to controlled servers and download malware or hand over credentials.

## When it applies

- Shared Wi-Fi networks or VLANs without inspection.
- Captures with duplicate ARP replies.
- DNS pointing to an unexpected IP.
- HTTP downloads of updates or installers.
- Traffic from a host that is not the gateway.

## Procedure

1. Count ARP requests and replies per MAC/IP.
2. Identify duplicate MACs for the gateway IP.
3. Review DNS queries and responses.
4. Compare the resolved IP with the legitimate one.
5. Extract the downloaded file and analyze it.

```bash
tshark -r capture.pcap -Y arp -T fields -e arp.opcode -e arp.src.proto_ipv4 -e arp.src.hw_mac | sort | uniq -c
tshark -r capture.pcap -Y 'dns.flags.response == 1' -T fields -e dns.qry.name -e dns.a
```

## Variants

- ARP spoofing of the gateway and the victim.
- DNS spoofing with forged replies.
- Rogue DHCP assigning a malicious gateway.
- Transparent proxy to intercept HTTP.
- SSL stripping when the site does not enforce HTTPS.

## Limitations

- The network must allow ARP broadcasts.
- Dynamic ARP Inspection or port security blocks it.
- HSTS and valid certificates limit impact.
- The attacker must be on the same segment.

## Mitigation and detection

- Enable Dynamic ARP Inspection and DHCP snooping.
- Use DNSSEC, DNS over HTTPS and a controlled resolver.
- Segment the network and avoid open Wi-Fi for work.
- Alert on duplicate MACs, gateway changes and newly registered domains.

## References

- <https://attack.mitre.org/techniques/T1557/002/>
- <https://attack.mitre.org/techniques/T1557/001/>
- <https://www.rfc-editor.org/rfc/rfc826.html>
- <https://www.wireshark.org/docs/wsug_html_chunked/>
