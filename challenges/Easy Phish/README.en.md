---
challenge: Easy Phish
type: OSINT
difficulty: Very Easy
platform: Hack The Box
state: Retired
tags: [osint, phishing, dns, spf, dmarc]
---

# Easy Phish — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

## TL;DR

This challenge has no attacker infrastructure: the question is **why** fake emails from `secure-startup.com` are not flagged as spam. The answer is in the domain's own DNS records — an **SPF** ending in `?all` (neutral, not `-all`) and a **DMARC** record with `p=none`. Each record also carries half the flag.

## Brief

"Customers of secure-startup.com have been receiving some very convincing phishing emails, can you figure out why?" No binary, no web app: just a domain and the hint that mail authentication is broken.

## Recon

```bash
dig +short TXT secure-startup.com
dig +short TXT _dmarc.secure-startup.com
dig +short MX secure-startup.com
```

```text
"v=spf1 a mx ?all - HTB{RIP_SPF_Always_2nd"
"v=DMARC1;p=none;_F1ddl3_2_DMARC}"
```

## Analysis

- **SPF**: `?all` means *neutral*. A receiver cannot claim the sender is authorised, but it does not reject it either; with `-all` (fail) the spoofed mail would have been marked. The `a`/`mx` mechanisms authorise only the domain's own hosts.
- **DMARC**: `p=none` asks for reports but gives receivers **no instruction to reject**. Without alignment enforcement or `quarantine`/`reject`, spoofing goes through.
- **DKIM**: no published record, so there is no second barrier to compensate.

The flag is split across the two TXT records: concatenate in order (SPF first, DMARC second).

## Exploitation

```bash
dig +short TXT secure-startup.com | tr -d '"'
dig +short TXT _dmarc.secure-startup.com | tr -d '"'
# join both halves inside HTB{...}
```

## Evidence

- `dig` output with the SPF and DMARC values (redacted in this writeup).
- The explanation of why `?all` and `p=none` allow the impersonation.

## Lessons

- **`?all` protects nothing**: only `-all` states that no other host may send for the domain.
- **`p=none` is monitor mode**: without `quarantine`/`reject`, DMARC stops nothing.
- SPF without DKIM or DMARC leaves the door open: the three complement each other.
- The flag inside the TXT records is a challenge trick; in the real world the finding is the policy, not the string.

## Mitigation and detection

- Publish `v=spf1 ... -all` with every legitimate sender (SaaS included) and watch the 10-DNS-lookup limit.
- DMARC at `p=quarantine` or `p=reject` with `rua`/`ruf` and strict alignment.
- DKIM signing all outbound mail.
- Detection: mail whose `Authentication-Results` shows `spf=neutral` or `dmarc=none` for your own domain.

## References

- [RFC 7208 (SPF)](https://www.rfc-editor.org/rfc/rfc7208)
- [RFC 7489 (DMARC)](https://www.rfc-editor.org/rfc/rfc7489)
- [phishing-infrastructure](../../knowledge/osint/phishing-infrastructure.md)
