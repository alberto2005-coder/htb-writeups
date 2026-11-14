---
topic: Data exfiltration
tags: [general, exfiltration, dns, http, smb, dlp]
---

# Data exfiltration

**English** | [🇪🇸 Español](data-exfiltration.md)

## Concept

Exfiltration extracts data from a compromised environment over allowed channels: HTTP/S, DNS, SMB, email or cloud storage. Analysis looks for anomalous volume, destination, encoding and timing, not just a suspicious connection.

## When it applies

- Large transfers to an external host.
- DNS queries with encoded strings.
- Use of a webhook, pastebin or bucket.
- Data movement before encryption or deletion.

## Procedure

1. Identify sensitive data and its location.
2. Review outbound connections and volumes.
3. Analyse DNS, HTTP and SMB for encoding.
4. Correlate with processes and accounts.
5. Document destination, size and period.

```bash
tcpdump -r capture.pcap -nn 'port 53 or port 80 or port 443'
tshark -r capture.pcap -Y 'dns.qry.name contains "<DOMAIN>"'
```

## Variants

- DNS tunnelling with encoded subdomains.
- HTTP POST to a webhook.
- Copy to an S3 bucket or a shared resource.
- Exfiltration through email or messaging.

## Limitations

- Traffic may be encrypted.
- Volume may be split into small transfers.
- Legitimate destinations can hide the activity.
- Without endpoint telemetry, the origin is hard to attribute.

## Mitigation and detection

- Apply DLP and restrict destinations.
- Monitor volumes, DNS and new connections.
- Block unapproved webhooks and storage.
- Alert on bulk compression and encryption before egress.

## References

- <https://attack.mitre.org/techniques/T1041/>
- <https://attack.mitre.org/techniques/T1048/003/>
- <https://www.cisa.gov/resources-tools/resources/data-loss-prevention>
