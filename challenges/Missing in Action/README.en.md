---
challenge: Missing in Action
type: OSINT
difficulty: Easy
platform: Hack The Box
state: Retired
tags: [osint, social-media, google-dorks, geolocation]
---

# Missing in Action — Hack The Box (Challenge)

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Documented challenge; no real personal data.
> The names and profiles in the brief are fictional. No accounts are linked and no identifiers are published.

## TL;DR

The brief gives a name and a city: a person disappeared during a business trip. Searching the name on LinkedIn leads to the company; the company's Twitter account leads to a Foursquare profile with reviews and locations. A dork combining the name and company finds a post containing the flag.

## Brief and surface

- OSINT, Easy, retired.
- No files are provided: only a description with a name, city and context.
- The goal is to locate the person's public activity.

## Recon

Use a browser and search engines, not scanning tools. The first query combines name and city:

```text
"<name>" "<city>"
```

The main result is a LinkedIn profile. The company listed there is the hint for the next hop.

## Analysis

The company has a Twitter presence. Its posts link to Foursquare, where reviews and visited places appear. That combination reconstructs the trip.

```text
site:twitter.com "<company>"
site:foursquare.com "<company>"
```

With the company and name, try more specific dorks:

```text
"<name>" "<company>" site:*
"<name>" "<city>" "flag"
```

The flag is in a public post tied to the profile; no login or interaction is needed.

## The bug

The person reused the same name and company across networks and posted travel activity without restricting the audience. Correlating identity across LinkedIn, Twitter and Foursquare is enough to reach the content. The challenge shows how a digital footprint is built from small posts.

## Local reproduction

There is no exploit to run. Document the query sequence and keep a redacted screenshot of each hop. Use an isolated browser and do not sign in with personal accounts.

```text
1. name + city -> LinkedIn -> company
2. company -> Twitter -> Foursquare link
3. name + company + dork -> post with the flag
```

## Exploitation

"Exploitation" is passive OSINT: send no messages, do not follow the person and do not access private content. Copy the flag from the public post and verify it on the platform.

## Evidence

- LinkedIn profile screenshot with personal data blurred.
- Company account and Foursquare link screenshot.
- Post with the flag redacted.

## Lessons learned

- Cross-network identity correlation is stronger than a single search.
- Dorks with company and name reduce noise.
- Public geolocation can reconstruct an itinerary.
- Ethical OSINT stays within public information and does not contact the person.

## Mitigations and detection

- Review account privacy and separate personal and professional identity.
- Do not post real-time locations or trip details.
- Use different aliases per community where possible.
- Detection: alerts for your own name and periodic public-footprint audits.

## References

- <https://7rocky.github.io/en/ctf/htb-challenges/osint/missing-in-action/>
- <https://www.google.com/search?q=Google+advanced+search+operators>
- <https://osintframework.com/>
