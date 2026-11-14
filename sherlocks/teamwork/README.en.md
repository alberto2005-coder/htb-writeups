---
sherlock: TeamWork
category: Threat Intelligence
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [threat-intelligence, osint, nft, infrastructure, typosquatting]
---

# TeamWork — Hack The Box (Sherlock)

**English** | [🇪🇸 Español](README.md)

> **Status:** Retired. Methodological writeup; no literal answers or real data.

## Scenario

A supposedly charitable group promotes an NFT project and asks users to connect wallets. A domain, screenshots and a message archive are provided; the task is to attribute the infrastructure and modus operandi.

## Evidence

- Domain, certificates and DNS records.
- Site screenshots and social-media messages.
- ZIP archive with the cloned site.

```bash
whois <DOMAIN>
dig +short <DOMAIN> A
curl -sI https://<DOMAIN>/
```

## Investigation

### 1. Site fingerprint

Compare resources, favicon and certificates with the legitimate project. Donation links and the wallet-connect flow reveal the objective.

```bash
curl -s https://<DOMAIN>/ | grep -Eo 'https?://[^" ]+' | sort -u
```

### 2. Infrastructure

DNS, ASN and certificates link domains. Look for typographic variants and accounts with the same handle. Do not interact with wallets or send funds.

```bash
curl -s 'https://crt.sh/?q=%25.<DOMAIN>&output=json'
```

### 3. Narrative and attribution

Compare messages, filenames and ZIP metadata with known campaigns. State attribution with confidence and evidence, not absolute certainty.

## Conclusions

- The site imitates a brand and diverts funds.
- Certificates and ASN group the infrastructure.
- The charitable narrative lowers suspicion.
- Attribution is probable, not definitive.

## Lessons

- OSINT requires not interacting with the target.
- Certificates are a pivot source.
- The cloned archive preserves paths and metadata.
- Intelligence is documented with confidence levels.

## References

- <https://www.hackthebox.com/sherlocks>
- <https://attack.mitre.org/techniques/T1583/001/>
- <https://attack.mitre.org/techniques/T1566/>
