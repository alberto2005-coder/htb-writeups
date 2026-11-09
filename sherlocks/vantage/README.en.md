---
sherlock: Vantage
domain: DFIR / Network
difficulty: Very Easy
platform: Hack The Box
evidence: Two captures: web server and private-cloud controller
tools: [Wireshark, tshark, CyberChef]
---

# Vantage — Hack The Box

**English** | [🇪🇸 Español](README.md)

> Defensive investigation. No platform answers copied.

## Scenario

A small company moved resources into a **private cloud**; the development web server kept the redirect to the dashboard. An alleged attacker writes claiming the data leaked. Two captures are provided: the web server's and the cloud controller's.

## Evidence

- `web-server_2025-07-01.pcap` and `controller_2025-07-01.pcap`.

## Method

1. **Discovery phase**: thousands of `GET /` with a different `Host` each time, walking a wordlist alphabetically. That is **subdomain enumeration**, not browsing.

```bash
tshark -r web-server_2025-07-01.pcap -Y 'http.request' -T fields -e http.host | sort | uniq -c | sort -rn | head
```

2. **Exploitation phase**: the `Host` locks onto one subdomain and `POST`s to a login begin, followed by normal navigation. That is the entry point.

3. **Correlate both captures**: what is downloaded on the web side shows up later on the controller side; without crossing them the impact is unclear.

```bash
tshark -r controller_2025-07-01.pcap -q -z conv,ip
```

4. **Services involved**: the controller shows cloud API calls; identifying which one handles authentication (Keystone in OpenStack) explains the access.

5. **Timeline**: order both files by `frame.time` and mark enumeration, login and first download.

## What it teaches

- Enumeration and exploitation have distinct signatures: volume and diversity versus repetition against one target.
- Two captures beat one: the web side shows the entry, the controller shows the reach.
- A `Host` that changes on every request is the clearest sign of *vhost fuzzing*.

## Pitfalls

- **TLS noise**: without keys, metadata only; focus on HTTP and internal flows.
- **Time zones**: the two files may disagree; normalise before crossing them.
- **Wildcard subdomains**: if everything answers 200, status codes tell nothing; compare response sizes.
