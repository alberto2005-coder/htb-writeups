---
sherlock: Trent
domain: DFIR
difficulty: Medium
platform: Hack The Box
state: Retired
tags: [dfir, pcap, router, firmware, command-injection, cve-2024-28353]
---

# Trent — Hack The Box

**English** | [🇪🇸 Español](README.md)

> **State:** Retired. Methodology note; no literal platform answers.

## Scenario

The SOC detects lateral movement against a branch router. The only evidence is a capture of about 17 minutes taken inside the network. The job is to identify the attacking host, the firmware vulnerability and what ran afterwards.

## Evidence

```text
trent/trent.pcap        Linux cooked-mode capture, ~81,000 packets
```

```bash
capinfos trent.pcap
tshark -r trent.pcap -q -z endpoints,ip
```

## Investigation

### 1. Inventory and triage

`capinfos` gives duration and packet count; `endpoints` reveals three or four hosts. The router is the gateway and the internal host generating the most HTTP requests is the suspect. Filter HTTP requests to the admin panel.

```bash
tshark -r trent.pcap -Y 'http.request && ip.dst==192.168.10.1' -T fields -e frame.time -e ip.src -e http.request.method -e http.request.uri | head
```

### 2. Timeline

First a login on the router's web panel, then a `POST /apply.cgi` with the `usbapps.config.smb_admin_name` parameter loaded with metacharacters. The response confirms execution. Shortly after, the router downloads a script and opens an outbound connection to the C2.

### 3. Key artefact

The command injection in `apply.cgi` is **CVE-2024-28353** in the TRENDnet TEW-827DRU firmware: the `smb_admin_name` field is passed to a shell unsanitised. Following the download's TCP stream reads the script, which launches a reverse shell to `35.159.25.253:41143`. The firmware version appears in the HTTP responses and confirms the CVE.

```bash
tshark -r trent.pcap -Y 'http.request.method=="POST" && http.request.uri contains "apply.cgi"' -T fields -e http.file_data | head -c 600
```

## Conclusions

- Entry: router panel credentials and an authenticated command injection in `apply.cgi`.
- Vulnerability: CVE-2024-28353, missing sanitisation of `usbapps.config.smb_admin_name`.
- Action: script download and reverse shell to `35.159.25.253:41143`.
- IOCs: C2 IP and port, script path and the parameter used in the POST.
- Persistence: not visible in the capture; the router does not reboot in the window.

## Lessons

- Network-device admin panels are internal attack surface: a successful login followed by `apply.cgi` deserves review.
- The internal capture is enough to identify the CVE when firmware versions are recorded in responses.
- A compromised router provides internet egress without the proxy: the outbound connection is the most useful IOC.
- Mitigation: update firmware, change default credentials and segment network management into an isolated VLAN.
- Detection: POSTs to `apply.cgi` with metacharacters, script downloads from the router and outbound connections from network devices.
- What is missing: router syslog and NetFlow to confirm the volume sent.

MITRE: T1190 (exploit public-facing application), T1059.004 (Unix shell), T1105 (ingress tool transfer), T1071.001 (web protocols).
