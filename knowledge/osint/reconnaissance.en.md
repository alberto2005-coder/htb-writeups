---
topic: OSINT reconnaissance
tags: [osint, reconnaissance, whois, certificates, github, shodan]
---

# OSINT reconnaissance

**English** | [🇪🇸 Español](reconnaissance.md)

## Concept

OSINT collects public information about an organisation, its domains, employees, technologies and exposures. The goal is a verifiable inventory without intrusive interaction with the target.

## When it applies

- An organisation's domains and subdomains.
- Public repositories and leaks.
- Document and image metadata.
- Exposed services indexed by search engines.

## Procedure

1. Define scope and rules of engagement.
2. Enumerate domains, certificates and DNS.
3. Review GitHub, leaks and metadata.
4. Look for technologies and exposed services.
5. Validate and prioritise findings.

```bash
whois <DOMAIN>
curl -s 'https://crt.sh/?q=%25.<DOMAIN>&output=json' | jq -r '.[].name_value' | sort -u
theHarvester -d <DOMAIN> -b crtsh,bing
```

## Variants

- Certificate transparency for subdomains.
- GitHub dorking and secret searches.
- Shodan/Censys for exposed services.
- EXIF metadata and office documents.

## Limitations

- Information may be outdated.
- Results may include unrelated domains.
- Not every public finding is exploitable.
- Legal scope must be authorised.

## Mitigation and detection

- Minimise public exposure of services.
- Remove secrets from repositories and metadata.
- Monitor certificates and lookalike domains.
- Review the digital footprint periodically.

## References

- <https://attack.mitre.org/techniques/T1593/>
- <https://crt.sh/>
- <https://osintframework.com/>
